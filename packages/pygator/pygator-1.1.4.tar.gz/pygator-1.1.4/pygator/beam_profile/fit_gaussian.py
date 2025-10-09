import numpy as np
from scipy.optimize import curve_fit
from scipy.ndimage import center_of_mass

def gaussian_2d(coords, A, x0, y0, w_x, w_y, B, theta=0):
    x, y = coords
    xr = (x - x0) * np.cos(theta) - (y - y0) * np.sin(theta)
    yr = (x - x0) * np.sin(theta) + (y - y0) * np.cos(theta)
    return (A * np.exp(-2 * ((xr / w_x)**2 + (yr / w_y)**2)) + B).ravel()


def fit_gaussian(image):
    y = np.arange(image.shape[0])
    x = np.arange(image.shape[1])
    x, y = np.meshgrid(x, y)

    A_init = np.max(image) - np.min(image)
    x0_init = image.shape[1] / 2
    y0_init = image.shape[0] / 2
    w_x_init = image.shape[1] / 4
    w_y_init = image.shape[0] / 4
    B_init = np.min(image)
    theta_init=0

    initial_guess = (A_init, x0_init, y0_init, w_x_init, w_y_init, B_init,theta_init)

    popt, _ = curve_fit(gaussian_2d, (x, y), image.ravel(), p0=initial_guess)

    return popt


def fit_gaussian_roi(image, roi_size=100, downsample=1, meshgrid_cache={},warn_once=[False],theta_user=0):
    """
    Fit a 2D Gaussian to a small ROI around the brightest pixel.

    Parameters:
    - image: 2D numpy array (grayscale image)
    - roi_size: size of the square ROI (must be even-ish and small, e.g., 50-150)
    - downsample: integer factor to downsample the image for fitting
    - meshgrid_cache: dict to store cached meshgrids to avoid recomputation

    Returns:
    - params: (A, x0, y0, w_x, w_y, B) with coordinates scaled back to full-res
    """
    # --- Check for saturation ---
    bit_depth_max = 255  # adjust as needed
    saturated_mask = image >= bit_depth_max
    num_saturated = np.sum(saturated_mask)

    if num_saturated > 0 and not warn_once[0]:
        total_pixels = image.size
        percent_saturated = 100.0 * num_saturated / total_pixels
        print(f"Warning: {num_saturated} pixels saturated "
              f"({percent_saturated:.3f}% of image). Max = {np.max(image)}")
        warn_once[0] = True   # remember that we already warned

    # Step 1: Find max pixel for ROI center
    # Step 1: Find COM for ROI center
    com = center_of_mass(image)
    xcom = com[1]
    ycom = com[0]
    half = roi_size // 2
    y1, y2 = max(0, round(ycom) - half), min(image.shape[0], round(ycom) + half)
    x1, x2 = max(0, round(xcom) - half), min(image.shape[1], round(xcom) + half)
    cropped = image[y1:y2, x1:x2]
    
    # Step 2: Downsample if needed
    if downsample > 1:
        import cv2
        cropped = cv2.resize(cropped, (cropped.shape[1] // downsample, cropped.shape[0] // downsample),
                             interpolation=cv2.INTER_AREA)

    # Step 3: Meshgrid caching
    h, w = cropped.shape
    if (h, w) not in meshgrid_cache:
        y = np.arange(h)
        x = np.arange(w)
        meshgrid_cache[(h, w)] = np.meshgrid(x, y)
    xg, yg = meshgrid_cache[(h, w)]

    # Step 4: Initial guess
    A_init = np.max(cropped) - np.min(cropped)
    x0_init = w / 2
    y0_init = h / 2
    w_x_init = w / 4
    w_y_init = h / 4
    B_init = np.min(cropped)
    theta_init=0

    # --- Fit with fixed user theta ---
    theta_user_rad = theta_user * np.pi / 180
    fitfun_fixed = lambda coords, A, x0, y0, w_x, w_y, B: gaussian_2d(
        coords, A, x0, y0, w_x, w_y, B, theta=theta_user_rad
    )

    bounds_lower = (0,   -np.inf, -np.inf, 0,   0,   -np.inf) 
    bounds_upper = (np.inf, np.inf,  np.inf, np.inf, np.inf, np.inf)

    popt_fixed, _ = curve_fit(
        fitfun_fixed,
        (xg, yg),
        cropped.ravel(),
        p0=(A_init, x0_init, y0_init, w_x_init, w_y_init, B_init),
        bounds=(bounds_lower, bounds_upper),
        maxfev=10000
    )
    A, x0, y0, w_x, w_y, B = popt_fixed

    # --- Fit with free theta (diagnostic only) ---
    try:
        bounds_lower = (0,   -np.inf, -np.inf, 0,   0,   -np.inf, 0)
        bounds_upper = (np.inf, np.inf,  np.inf, np.inf, np.inf, np.inf,  np.pi)

        popt_free, _ = curve_fit(
            gaussian_2d,
            (xg, yg),
            cropped.ravel(),
            p0=(A_init, x0_init, y0_init, w_x_init, w_y_init, B_init, theta_init),
            bounds=(bounds_lower, bounds_upper),
            maxfev=10000
        )
        theta_fit = popt_free[-1]
    except Exception:
        theta_fit = np.nan  # fallback if free fit fails

    # Rescale to full image coords
    x0 = x1 + x0 * downsample
    y0 = y1 + y0 * downsample
    w_x *= downsample
    w_y *= downsample

    return (A, x0, y0, w_x, w_y, B, theta_fit*180/np.pi, theta_user_rad)



def image_pixel_avg(image, roi_size=10, warn_once=[False]):
    """
    Give the average pixel grayscale for image parameter in an ROI of 10x10 pixels
    centered in the "center of mass" of the image".

    Parameters:
    - image: 2D numpy array (grayscale image)
    - roi_size: size of the square ROI (must be even-ish and small, e.g., 50-150)

    Returns:
    - px_avg (average pixel grayscale for image parameter)
    - com (Center of mass coordinate in the image)
    - bpc (Coordinate of brightest pixel in the image)
    - num_sat (Number of saturated pixels inside the 10x10 ROI)
    - diff (The distance between the com and the bpc; a tuple, it gives the 
    difference between y coordinates and difference between x coordinates 
    (delta_y,delta_x))
    """


    # Step 1: Find the center of mass of the image
    com = center_of_mass(image)
    xcom = com[1]
    ycom = com[0]
    # Step 2: Create ROI approximately centered on COM
    half = roi_size // 2
    y1, y2 = max(0, round(ycom) - half), min(image.shape[0], round(ycom) + half)
    x1, x2 = max(0, round(xcom) - half), min(image.shape[1], round(xcom) + half)
    cropped = image[y1:y2, x1:x2]

    # --- Check for saturation inside 10x10 ROI ---
    bit_depth_max = 255  # adjust as needed
    saturated_mask = cropped >= bit_depth_max
    num_saturated = np.sum(saturated_mask)

    if num_saturated > 0 and not warn_once[0]:
        total_pixels = cropped.size
        percent_saturated = 100.0 * num_saturated / total_pixels
        print(f"Warning (inside 10x10 ROI): {num_saturated} pixels saturated "
              f"({percent_saturated:.3f}% of image). Max = {np.max(cropped)}")
        warn_once[0] = True   # remember that we already warned

    #{h, w = image.shape
    #if (h, w) not in meshgrid_cache:
        #y = np.arange(h)
        #x = np.arange(w)
        #meshgrid_cache[(h, w)] = np.meshgrid(x, y)
    #{xg, yg = meshgrid_cache[(h, w)]

    # Step 3: Find the average pixel grayscale in this small ROI centered at 
    # the COM
    px_avg = np.mean(cropped)

    # Find brightest pixel coordinate
    bpc = np.unravel_index(np.argmax(image), image.shape)
    xbp = bpc[1]
    ybp = bpc[0]

    # Find the distance between the brightest pixel and the center of mass
    # The first value in the tuple is the distance between their y coordinates
    # The second value is the distance between their x coordinates
    diff = np.abs(np.array(bpc)-np.array(com))
    delta_x = diff[1]
    delta_y = diff[0]
    
    


    return (px_avg,xcom,ycom,xbp,ybp,num_saturated,delta_x,delta_y)
