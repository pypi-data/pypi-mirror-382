import cv2
import numpy as np
import argparse
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from .fit_gaussian import fit_gaussian_roi, gaussian_2d
from .live_camera import get_camera_and_start

def draw_text(image, text, pos=(10, 20), color=(255,)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, text, pos, font, 0.5, color, 1)

def live_visualize_beam(roi_size=200, downsample=2, exposure='auto', gain='auto', mode='gray'):
    # Connect to camera
    cam, cam_list, system = get_camera_and_start(exposure, gain)
    if cam is None:
        return

    meshgrid_cache = {}

    plt.ion()
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    try:
        while True:
            # Grab frame
            image_result = cam.GetNextImage()
            if image_result.IsIncomplete():
                print("Incomplete image:", image_result.GetImageStatus())
                image_result.Release()
                continue

            img = image_result.GetNDArray().copy()
            image_result.Release()

            # Fit Gaussian on ROI
            try:
                params = fit_gaussian_roi(img, roi_size=roi_size,
                                          downsample=downsample,
                                          meshgrid_cache=meshgrid_cache)
                A, x0, y0, w_x, w_y, B,theta_fit ,theta_user= params

                # Extract ROI
                max_y, max_x = np.unravel_index(np.argmax(img), img.shape)
                half = roi_size // 2
                y1, y2 = max(0, max_y - half), min(img.shape[0], max_y + half)
                x1, x2 = max(0, max_x - half), min(img.shape[1], max_x + half)
                cropped = img[y1:y2, x1:x2]

                # Meshgrid for ROI
                h, w = cropped.shape
                y = np.arange(h)
                x = np.arange(w)
                xg, yg = np.meshgrid(x, y)
                params=params[:-1]
                # Fitted Gaussian
                fitted = gaussian_2d((xg, yg), *params).reshape(cropped.shape)

                # === OpenCV window ===
                if mode == 'heatmap':
                    display_img = cv2.applyColorMap(img, cv2.COLORMAP_JET)
                    text_color = (255, 255, 255)
                else:
                    display_img = img.copy()
                    text_color = (255,)

                draw_text(display_img, f"A = {A:.2f}", (10, 20), color=text_color)
                draw_text(display_img, f"B = {B:.2f}", (10, 40), color=text_color)
                draw_text(display_img, f"w_x = {w_x:.1f} px", (10, 60), color=text_color)
                draw_text(display_img, f"w_y = {w_y:.1f} px", (10, 80), color=text_color)
                cv2.imshow("Beam Profile (2D)", display_img)

                # === Matplotlib 3D plot ===
                ax.cla()
                ax.plot_surface(xg, yg, cropped, cmap="viridis", alpha=0.6)
                ax.plot_wireframe(xg, yg, fitted, color="red", linewidth=0.5)
                ax.set_title("Live Beam Fit (ROI + Gaussian)")
                ax.set_xlabel("X [px]")
                ax.set_ylabel("Y [px]")
                ax.set_zlabel("Intensity")
                plt.pause(0.01)

            except Exception as e:
                print("Fit failed:", e)
                continue

            # Quit on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
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

if __name__ == "__main__":
    """python live_visualize_beam.py --roi-size 300 --downsample 2 --mode heatmap

    """
    parser = argparse.ArgumentParser(description="Live 2D+3D Gaussian visualization of beam ROI")
    parser.add_argument("--roi-size", type=int, default=200, help="ROI size in pixels")
    parser.add_argument("--downsample", type=int, default=2, help="Downsampling factor")
    parser.add_argument("--exposure", default="auto", help="Camera exposure (µs)")
    parser.add_argument("--gain", default="auto", help="Camera gain (dB)")
    parser.add_argument("--mode", choices=["gray", "heatmap"], default="gray",
                        help="Display mode for 2D window")
    args = parser.parse_args()

    live_visualize_beam(
        roi_size=args.roi_size,
        downsample=args.downsample,
        exposure=args.exposure,
        gain=args.gain,
        mode=args.mode
    )
