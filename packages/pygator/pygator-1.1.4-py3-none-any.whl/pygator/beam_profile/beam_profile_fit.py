import cv2
import numpy as np
import argparse
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import simpledialog, messagebox
from .fit_gaussian import fit_gaussian_roi, gaussian_2d
from .live_camera import get_camera_and_start
from pygator.module import fit_beam_profile_ODR
import csv
import PySpin

def draw_text(image, text, pos=(10, 20), color=(255,)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, text, pos, font, 0.5, color, 1)

def get_distance_input():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    user_input = simpledialog.askstring("Distance Moved (inches)", 
                                        "Enter distance moved from previous position (inches, e.g. 1.0):")
    root.destroy()
    return user_input

def ask_to_save():
    root = tk.Tk()
    root.withdraw()
    response = messagebox.askyesno("Save Data", "Save recorded data to CSV?")
    root.destroy()
    return response

def draw_grid(img, step=50, color=(100, 100, 100), thickness=1):
    """Draws a grid over the entire image."""
    h, w = img.shape[:2]

    # Vertical lines
    for x in range(0, w, step):
        cv2.line(img, (x, 0), (x, h), color, thickness)

    # Horizontal lines
    for y in range(0, h, step):
        cv2.line(img, (0, y), (w, y), color, thickness)


def beam_profile_fit(roi_size=300, downsample=2, exposure='auto', gain='auto',
                     pixel_size_um=6.9, output_file="beam_profile.csv", mode="gray",theta_val=0
                     ,scaling_factor=1):

    pixel_size_m = pixel_size_um * 1e-6
    cam, cam_list, system = get_camera_and_start(exposure, gain)
    if cam is None:
        return

    theta_val = float(theta_val)  # ensure numeric
    theta_step = 1.0  # degrees per key press
    z_list, wx_list, wy_list, wx_std_list, wy_std_list, theta_fit_list, A_list, B_list  = [], [], [], [], [], [], [], []
    wx_temp, wy_temp = [], []
    meshgrid_cache = {}
    z_position = 0.0

    print("Live beam profiling started. Press:")
    print("  [r] Record current sample (adds to buffer)")
    print("  [R] Finalize buffer (mean/std saved to dataset)")
    print("  [n] Move camera (input distance in inches)")
    print("  [[] Decreases the true coordinate rotation angle by 1 degree")
    print("  []] Increase the true coordinate rotation angle by 1 degree")
    print("  [f] Fit data and finish")
    print("  [q] Quit without fitting")


    plt.ion()
    plt.figure("Beam Width Live Plot")

    try:
        recording = False
        plt.ion()
        residual_fig,residual_ax=plt.subplots()
        residual_im=None
        while True:
                # Try to grab a frame
            try:
                image_result = cam.GetNextImage()
            except Exception as e:
                print(f"Warning: Camera read failed (camera may be disconnected): {e}")

                # Save buffered data to a temporary CSV
                temp_file = output_file.replace(".csv", "_disconnected_backup.csv")
                if len(z_list) > 0:
                    with open(temp_file, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(["z [m]", "wx [m]", "wy [m]", "wx_std [m]", "wy_std [m]", "theta_fit [deg]", "A [grayscale unit]", "B [grayscale unit]"])
                        for i in range(len(z_list)):
                            writer.writerow([z_list[i], wx_list[i], wy_list[i], wx_std_list[i], wy_std_list[i], theta_fit_list[i], A_list[i], B_list[i]])
                    print(f"Partial data saved to {temp_file}")

                break  # Exit the loop gracefully

            if image_result.IsIncomplete():
                print("Incomplete image:", image_result.GetImageStatus())
                image_result.Release()
                continue

            try:
                img = image_result.GetNDArray().copy()
            except Exception as e:
                print("Error reading image:", e)
                image_result.Release()
                continue

            image_result.Release()

            try:
                params = fit_gaussian_roi(img, roi_size=roi_size, downsample=downsample, meshgrid_cache=meshgrid_cache,theta_user=theta_val)
                x0, y0 = int(params[1]), int(params[2])
                half = roi_size // 2
                top_left = (max(0, x0 - half), max(0, y0 - half))
                bottom_right = (min(img.shape[1], x0 + half), min(img.shape[0], y0 + half))

                w_x_px = params[3]
                w_y_px = params[4]

                w_x_m = w_x_px * pixel_size_m/scaling_factor #1.13 scaling factor by comparing the FLIR camera to the WinCam
                w_y_m = w_y_px * pixel_size_m/scaling_factor
                A = params[0]

                # Use user theta for drawing
                theta = params[-1]
                theta_fit=params[-2] 

                # Choose mode-based display
                if mode == 'heatmap':
                    display_img = cv2.applyColorMap(img, cv2.COLORMAP_JET)
                    rect_color = (255, 0, 0)  # Blue rectangle
                    text_color = (255, 255, 255)
                    ellipse_color = (255, 255, 255)
                else:
                    display_img = img
                    rect_color = (200,)       # Light gray rectangle
                    text_color = (255,)
                    ellipse_color = (255,)
                
                #Adding a grid
                draw_grid(display_img, step=100, color=(100, 100, 100))  # gray grid
                # Draw ROI rectangle and ellipse
                cv2.rectangle(display_img, top_left, bottom_right, rect_color, 1)
                center = (x0, y0)
                axes = (int(params[3] * 2), int(params[4] * 2))
                cv2.ellipse(display_img, center, axes, 0, 0, 360, ellipse_color, 1)

                # Crosshair parameters
                # Use ROI size for line lengths
                Lx = (bottom_right[0] - top_left[0]) // 2  # half width
                Ly = (bottom_right[1] - top_left[1]) // 2  # half height

                # Function to rotate points
                def rotate_point(x, y, theta, x0=0, y0=0):
                    x_rot = (x) * np.cos(theta) + (y) * np.sin(theta) + x0
                    y_rot = -(x) * np.sin(theta) + (y) * np.cos(theta) + y0
                    return int(x_rot), int(y_rot)

                # Horizontal line (dashed approximation)
                num_dashes = 10
                for i in range(num_dashes):
                    start_frac = i / num_dashes
                    end_frac = (i + 0.5) / num_dashes
                    x_start = -Lx + 2 * Lx * start_frac
                    x_end   = -Lx + 2 * Lx * end_frac
                    y_start, y_end = 0, 0
                    pt1 = rotate_point(x_start, y_start, theta, x0, y0)
                    pt2 = rotate_point(x_end, y_end, theta, x0, y0)
                    cv2.line(display_img, pt1, pt2, (0, 0, 255), 1)

                # Vertical line (solid)
                pt1 = rotate_point(0, -Ly, theta, x0, y0)
                pt2 = rotate_point(0, Ly, theta, x0, y0)
                cv2.line(display_img, pt1, pt2, (0, 0, 255), 1)

                # Horizontal line (dashed approximation)
                num_dashes = 10
                for i in range(num_dashes):
                    start_frac = i / num_dashes
                    end_frac = (i + 0.5) / num_dashes
                    x_start = -Lx + 2 * Lx * start_frac
                    x_end   = -Lx + 2 * Lx * end_frac
                    y_start, y_end = 0, 0
                    pt1 = rotate_point(x_start, y_start, theta_fit, x0, y0)
                    pt2 = rotate_point(x_end, y_end, theta_fit, x0, y0)
                    cv2.line(display_img, pt1, pt2, (0, 255, 255), 1)

                # Vertical line (solid)
                pt1 = rotate_point(0, -Ly, theta_fit, x0, y0)
                pt2 = rotate_point(0, Ly, theta_fit, x0, y0)
                cv2.line(display_img, pt1, pt2, (0, 255, 255), 1)



                # Draw text
                draw_text(display_img, f"A = {A:.2f} Grayscale Unit", (10, 20), color=text_color)
                draw_text(display_img, f"w_x = {w_x_m*1e6:.2f} um", (10, 40), color=text_color)
                draw_text(display_img, f"w_y = {w_y_m*1e6:.2f} um", (10, 60), color=text_color)
                draw_text(display_img, f"B = {params[5]:.2f} Grayscale Unit", (10, 80), color=text_color)
                draw_text(display_img, f"z = {z_position*1000:.2f} mm", (10, 100), color=text_color)
                draw_text(display_img, f"Fit theta (Diagnostic only) = {(theta_fit*180/np.pi)%360:.2f} deg", (10, 120), color=text_color)
                draw_text(display_img, f"User theta = {theta*180/np.pi:.2f} deg", (10, 140), color=text_color)
                draw_text(display_img, f"x0,y0 = {x0} {y0}", (10, 160), color=text_color)



                # Let's open a 2nd window to plot the residual 
                # roi_data = img #[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
                X_fit = np.arange(img.shape[1])
                Y_fit = np.arange(img.shape[0])
                X, Y = np.meshgrid(X_fit, Y_fit)
                gaussian_fit_ROI=gaussian_2d((X,Y),params[0],params[1],params[2],params[3],params[4],params[5],theta).reshape(img.shape)
                # print("size roi",np.shape(roi_data),'size gaussian', np.shape(gaussian_fit_ROI))
                residual=img-gaussian_fit_ROI


                # Normalize residual to 0-255 for color mapping
                residual_norm = cv2.normalize(residual, None, 0, 255, cv2.NORM_MINMAX)
                residual_uint8 = np.uint8(residual_norm)
                residual_color = cv2.applyColorMap(residual_uint8, cv2.COLORMAP_JET)

                # create the colorbar
                h, w, _ = residual_color.shape
                bar_width = 100
                scale_factor = 1  # 90% of the height of residual
                bar_height = int(h * scale_factor)

                gradient = np.linspace(0, 255, bar_height).astype(np.uint8)
                gradient = np.tile(gradient[:, None], (1, bar_width))
                colorbar = cv2.applyColorMap(gradient, cv2.COLORMAP_JET)

                # Pad the colorbar to match residual height
                pad_top = (h - bar_height) // 2
                pad_bottom = h - bar_height - pad_top
                colorbar = cv2.copyMakeBorder(colorbar, pad_top, pad_bottom, 0, 0, cv2.BORDER_CONSTANT, value=[0,0,0])

                # printing min and max on the screen
                min_val, max_val = np.min(residual), np.max(residual)
                # print(h)
                cv2.putText(colorbar, f"Max: {max_val:.2f}", (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
                cv2.putText(colorbar, f"Min: {min_val:.2f}", (0, h-(int(h/4))), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

                # Concatenate colorbar to the right of the residual
                residual_display = cv2.hconcat([residual_color, colorbar])
                cv2.imshow("Residual Window", residual_display) # showing a window of the ROI size

            except Exception as e:
                print("Warning: Fit failed for this frame (beam may be absent or too faint). Skipping frame.")
                continue  # skip to next frame, no display or processing for this frame
            cv2.imshow('Beam Profile Fit Window', display_img)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('r'):
                recording = not recording
                print(f"Recording {'ON' if recording else 'OFF'}...")

            if recording:
                wx_temp.append(w_x_m)
                wy_temp.append(w_y_m)
                print(f"Buffered sample: wx={w_x_m*1e6:.2f} um, wy={w_y_m*1e6:.2f} um")

            elif key == ord('R'):
                if wx_temp:
                    w_x_mean = np.mean(wx_temp)
                    w_y_mean = np.mean(wy_temp)
                    w_x_std = max(np.std(wx_temp), 1e-6)
                    w_y_std = max(np.std(wy_temp), 1e-6)
                    wx_list.append(w_x_mean)
                    wy_list.append(w_y_mean)
                    wx_std_list.append(w_x_std)
                    wy_std_list.append(w_y_std)
                    z_list.append(z_position)
                    theta_fit_list.append(theta_fit%360)
                    A_list.append(A)
                    B_list.append(params[5])

                    print(f"Recorded batch: z={z_position:.3f} m, "
                          f"wx={w_x_mean*1e6:.2f}±{w_x_std*1e6:.2f} um, "
                          f"wy={w_y_mean*1e6:.2f}±{w_y_std*1e6:.2f} um, "
                          f"A = {A:.2f} grayscale unit, "
                          f"B = {params[5]:.2f} grayscale unit"
                          f"theta_fit={theta_fit:.2f} deg")

                    plt.clf()
                    plt.errorbar(z_list, np.array(wx_list)*1e6, yerr=np.array(wx_std_list)*1e6, fmt='o', label='wx', capsize=3)
                    plt.errorbar(z_list, np.array(wy_list)*1e6, yerr=np.array(wy_std_list)*1e6, fmt='o', label='wy', capsize=3)
                    plt.xlabel("z position [m]")
                    plt.ylabel("Beam width [um]")
                    plt.legend()
                    plt.title("Live Beam Width vs. z")
                    plt.tight_layout()
                    plt.draw()
                    plt.show(block=False)
                    plt.gcf().canvas.flush_events()
                    wx_temp.clear()
                    wy_temp.clear()

            elif key == ord('n'):
                distance_str = get_distance_input()
                try:
                    dz_inch = float(distance_str)
                    dz_m = dz_inch * 0.0254
                    z_position += dz_m
                    print(f"Moved by {dz_inch:.3f} in = {dz_m:.4f} m, new z = {z_position:.4f} m")
                except Exception:
                    print("Invalid distance.")

            elif key == ord('['):
                theta_val -= theta_step
                print(f"Theta adjusted: {theta_val:.2f} deg")

            elif key == ord(']'):
                theta_val += theta_step
                print(f"Theta adjusted: {theta_val:.2f} deg")

            elif key == ord('f'):
                if len(z_list) < 3:
                    print("Not enough points to fit.")
                    continue

                print("Fitting...")
                z = np.array(z_list)
                wx = np.array(wx_list)
                wy = np.array(wy_list)
                wx_std = np.array(wx_std_list)
                wy_std = np.array(wy_std_list)
                A_val = np.array(A_list)
                B_val = np.array(B_list)

                sol_x, sol_y = fit_beam_profile_ODR(
                    z, wx, z, wy,
                    w0guess=300e-6,
                    z0guess=z_list[0],
                    wx_std=wx_std,
                    wy_std=wy_std,
                    z_std=0.005,
                    title='Beam Profile',
                    print_results=True,
                    frac_err=0.02
                )

                q_x = f"{sol_x[1]:.4e} + i{sol_x[2]:.4e}"
                q_y = f"{sol_y[1]:.4e} + i{sol_y[2]:.4e}"
                print("q-parameter (x):", q_x)
                print("q-parameter (y):", q_y)

                plt.gcf()
                plt.text(0.05, 0.95, f"q_x = {q_x}", transform=plt.gca().transAxes,
                         verticalalignment='top', fontsize=8, color='blue')
                plt.text(0.05, 0.90, f"q_y = {q_y}", transform=plt.gca().transAxes,
                         verticalalignment='top', fontsize=8, color='green')
                plt.draw()

                if ask_to_save():
                    with open(output_file, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(["z [m]", "wx [m]", "wy [m]", "wx_std [m]", "wy_std [m]", "theta_fit [deg]", "A [grayscale unit]", "B [grayscale unit]"])
                        for i in range(len(z_list)):
                            writer.writerow([z_list[i], wx_list[i], wy_list[i], wx_std_list[i], wy_std_list[i], theta_fit_list[i], A_list[i], B_list[i]])
                        writer.writerow([])
                        writer.writerow(["q_x", f"'{q_x}'"])
                        writer.writerow(["q_y", f"'{q_y}'"])
                    print(f"Saved to {output_file}")
                break

            elif key == ord('p'):
                try:
                    nodemap = cam.GetNodeMap()

                    # Turn off auto exposure if it’s on
                    exposure_auto = PySpin.CEnumerationPtr(nodemap.GetNode("ExposureAuto"))
                    exposure_auto.SetIntValue(exposure_auto.GetEntryByName("Off").GetValue())

                    # Get the exposure node
                    exposure_time = PySpin.CFloatPtr(nodemap.GetNode("ExposureTime"))

                    if PySpin.IsAvailable(exposure_time) and PySpin.IsWritable(exposure_time):
                        new_exp_str = input("Enter new exposure time in µs: ")
                        try:
                            new_exp = float(new_exp_str)
                            # Clamp to camera limits
                            new_exp = min(max(new_exp, exposure_time.GetMin()), exposure_time.GetMax())
                            exposure_time.SetValue(new_exp)
                            print(f"Exposure manually set to {new_exp:.2f} µs")
                        except ValueError:
                            print("Invalid number, exposure unchanged.")
                    else:
                        print("ExposureTime node not available or not writable.")

                except Exception as e:
                    print(f"Failed to update exposure: {e}")


            elif key == ord('q'):
                print("Quit without fitting.")
                break

    finally:
        cam.EndAcquisition()
        cam.DeInit()
        del cam
        cam_list.Clear()
        system.ReleaseInstance()
        cv2.destroyAllWindows()
        plt.ioff()
        plt.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Live Gaussian beam profiling with camera.\n\n"
                                     "Example:\n"
                                     "  python beam_profile.py --roi-size 400 --downsample 2 --exposure auto --gain auto --pixel-size 6.9 --output my_beam_scan.csv",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--roi-size', type=int, default=300, help='ROI size in pixels')
    parser.add_argument('--downsample', type=int, default=2, help='Downsampling factor')
    parser.add_argument('--exposure', default='auto', help='Camera exposure (µs)')
    parser.add_argument('--gain', default='auto', help='Camera gain (dB)')
    parser.add_argument('--pixel-size', type=float, default=6.9, help='Pixel size in um (default 6.9)')
    parser.add_argument('--output', default="beam_profile.csv", help='Output CSV filename')
    parser.add_argument('--theta_val', type=float, default=0, help='angle to fit in deg')
    parser.add_argument('--scaling_factor', type=float, default=1, help='Scaling factor')
    parser.add_argument('--mode', choices=['gray', 'heatmap'], default='gray', help='Display mode for live camera (default: gray)')
    args = parser.parse_args()

    beam_profile_fit(
        roi_size=args.roi_size,
        downsample=args.downsample,
        exposure=args.exposure,
        gain=args.gain,
        pixel_size_um=args.pixel_size,
        output_file=args.output,
        theta_val=args.theta_val,
        scaling_factor=args.scaling_factor,
        mode=args.mode
    )