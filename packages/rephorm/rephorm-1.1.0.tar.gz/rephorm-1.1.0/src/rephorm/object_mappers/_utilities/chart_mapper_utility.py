import numpy as np

def process_bar_data(neg_data, pos_data, flattened):
    """
    Processes a flattened array by slicing it into chunks if its length differs
    from the target data arrays, then applies np.where per chunk and accumulates
    the negative or positive values into the corresponding data arrays.

    Args:
        neg_data (np.ndarray): negative data array.
        pos_data (np.ndarray): positive data array.
        flattened (np.ndarray): Flattened input array. (The actual series data)

    Returns:
        Tuple[np.ndarray, np.ndarray]: Updated negative and positive data arrays.
    """
    target_length = neg_data.shape[0]
    total_length = flattened.shape[0]

    # If equal, direct add
    if total_length == target_length:
        neg_data += np.where(flattened < 0, flattened, 0)
        pos_data += np.where(flattened > 0, flattened, 0)

    # If longer, break into chunks
    else:
        num_full_chunks = total_length // target_length

        for i in range(num_full_chunks):
            chunk = flattened[i * target_length : (i + 1) * target_length]
            neg_data += np.where(chunk < 0, chunk, 0)
            pos_data += np.where(chunk > 0, chunk, 0)

    return neg_data, pos_data
