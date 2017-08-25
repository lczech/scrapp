import os
import platform
import subprocess as sub
import urllib2

# ==================================================================================================
#     globals
# ==================================================================================================

# Get the dir where the script is located. The first variant expects that this is the main
# script. The second one might however break on a different OS. Needs to be tested.
# basedir = os.path.abspath( os.path.dirname(sys.argv[0]) )
basedir = os.path.abspath( os.path.realpath( os.path.join(
            os.path.dirname( os.path.abspath( os.path.realpath( __file__ ))), 
            "../deps/")))

# We currently expect all sub-programs to be located in sub-directories of our tool.
# Maybe this should go into a config file which also allows to use actual commands,
# in case that raxml-ng or mptp is actually installed on the system already.
prog_paths = {
    "alignment_splitter" : [basedir + "/genesis/bin/apps/"
                            ],
    "mptp"               : [basedir + "/mptp/bin/",         ],
    "raxml-ng"           : [basedir + "/raxml-ng/bin/",     
                            "https://github.com/amkozlov/raxml-ng/releases/download/0.4.1/raxml-ng_v0.4.1b"
                            ]
}

# ==================================================================================================
#     general util
# ==================================================================================================

def get_platform():
    """
    Return a descriptive tuple specifying platform info.
    """
    oper = platform.system().lower()
    arch = platform.machine()

    intrin = []
    tested_vecs = ["sse3", "avx", "avx2", "avx512"]

    FNULL = open(os.devnull, 'wb')

    for vec in tested_vecs:
        if sub.call(["grep", vec, "/proc/cpuinfo"], stdout=FNULL, stderr=FNULL) == 0:
            intrin = [vec] + intrin

    return (oper, arch, intrin)

def try_fetch(src_url, target_path):
    """
    Tries to download file at <src_url> to <target_path>.
    Returns file path on success, None otherwise.
    """
    written_filepath = ""
    try:
        f = urllib2.urlopen( src_url )
        print "downloading " + src_url

        if not os.path.exists(target_path):
            os.makedirs(target_path)

        # Open our local file for writing
        with open(os.path.join(target_path, os.path.basename(src_url)), "wb+") as local_file:
            written_filepath =  local_file.name
            print "... to " + written_filepath
            local_file.write(f.read())

    except urllib2.HTTPError, e:
        written_filepath = None
    except urllib2.URLError, e:
        written_filepath = None

    return written_filepath

def extract(filepath):
    """
    Extracts an archive based on its ending.
    """
    name, ending = os.path.splitext( filepath )
    if ending == ".zip":
        import zipfile
        zip_ref = zipfile.ZipFile( filepath, 'r' )
        zip_ref.extractall( os.path.dirname( filepath ) )
        zip_ref.close()
    else:
        raise RuntimeError( "Unrecognized extension: " + ending + " for file " + filepath )


def try_resolve_raxmlng(machine = get_platform()):
    """
    Tries to resolve dependency using a cascade of increasingly desperate measures.
    """
    entry = prog_paths["raxml-ng"]
    binpath = entry[0]

    (oper, arch, intrin) = machine

    # if binary doesn't exist, see if binary exists online
    url = entry[1]
    core_rax = "_" + oper + "_" + arch 
    base_rax_url = url + core_rax + ".zip"
    # mpi_rax_url = url + core_rax + "_MPI" + ".zip"

    print "Trying to download raxml-ng binary..." 
    filepath = try_fetch(base_rax_url, binpath)

    if filepath:
        print "Extracting..."
        extract(filepath)
        print "Done!"

    # TODO: set access modifier
    
    # TODO: case: cannot fetch by url -> try source
    
    print "Resolving raxml-ng was successful!"

def try_resolve_mptp(machine = get_platform()):
    return

def try_resolve_alignment_splitter(machine = get_platform()):
    return

def try_resolve(name, machine = get_platform()):
    print "Trying to resolve " + name + "..."
    if name == "raxml-ng":
        return try_resolve_raxmlng( machine )
    elif name == "mptp":
        return try_resolve_mptp( machine )
    elif name == "alignment_splitter":
        return try_resolve_alignment_splitter( machine )
    else:
        raise RuntimeError( "No such subprogram name: " + name )


# ==================================================================================================
#     Sub-Program Commands
# ==================================================================================================

def subprogram_commands():
    """
    Return a list of the sub program commands.
    """

    paths = {}

    for name, etc in prog_paths.iteritems():
        paths[name] = etc[0] + name
    
    return paths

def subprograms_exist( paths ):
    """
    Check whether all subprograms actually exists. Throw otherwise.
    """

    for name, cmd in paths.iteritems():
        if not os.path.isfile( cmd ):
            raise RuntimeError(
                "Subprogram '" + name + "' not found at '" + cmd + "'. Please run setup first."
            )


