import sys
import time
import canopy as cp


def main():

    # The imports are now more pandas-like:
    # import pyguess as cp
    # For now, the following functionalities are available as top-level imports. You need to update your
    # imports accordingly:
    #   cp.Field
    #   cp.Raster
    #   cp.RedSpec
    #   cp.get_source
    #   cp.make_raster
    #   cp.make_lines
    #   cp.concat2
    
    path_run = '/home/belda-d/data/pyguess_test_data/europe_LR_100p/output'
    file = 'agpp.out.gz'
    # Files can still be loaded directly:
    agpp = cp.Field.from_file(f'{path_run}/{file}')
    print(agpp)

    # But now there is a convenient source object to load and keep track of the fields automatically:
    run_europe = cp.get_source(path_run, 'lpjguess')

    # The source object contains info about the file format, description, units...
    print(run_europe)

    # Let's load some fields
    run_europe.load_field('anpp')
    run_europe.load_field('agpp')

    # If you print it now, you'll see that those two fields are marked as 'loaded'
    print(run_europe)

    # You can access the fields with 'dot' notation:
    print(run_europe.anpp)
    print(run_europe.agpp)

    # But you can't directly assign these attributes! This is for data protection. This will fail
    # run_europe.anpp = run_europe.anpp.red_space('av') # ERROR! Can't assing like this

    # You can do something like this instead:
    anpp_av = run_europe.anpp.red_space('av')
    # The original field will still be available in the source object. If you still insist on modifying the fields in the
    # source object, you can do:
    run_europe.anpp.red_space('av', inplace=True)
    # If you print the source object now, you'll see that it warns you that the anpp field has been modified:
    print(run_europe)
    # If this wasn't your intention, you can reload the field:
    run_europe.load_field('anpp')
    print(run_europe) # Reloaded: goes back to loaded but unmodified

    #Lastly, you can unload or 'drop' fields that you don't need anymore:
    run_europe.drop_field('anpp')
    print(run_europe)


if __name__== '__main__':
    sys.exit(main())

