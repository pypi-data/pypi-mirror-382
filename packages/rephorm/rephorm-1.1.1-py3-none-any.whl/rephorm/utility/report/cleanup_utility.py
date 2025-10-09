# make util funct cleanup later on, so less code regarding cleanup stuff. but call it here.
import os
import shutil

from rephorm.object_mappers._globals import reset_figure_map

def perform_cleanup(cleanup: bool = False, directory_path: str = None, base_file_path: str = None):

    reset_figure_map()

    try:
        # Remove tmp dir where pdf figures are stored
        if cleanup:
            shutil.rmtree(directory_path)
        # Remove base (initial) pdf
        os.remove(base_file_path)

    except Exception as e:
        print(f"Cleanup utility - error occurred: {e}")