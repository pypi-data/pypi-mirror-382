import os
import sys
import time
import subprocess
import re
from sys import platform



"""
Pre-requisite: Corresponding Cuda versions.
https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=24.04&target_type=deb_network

Additional packages for GPU with RAPIDS:
https://docs.rapids.ai/install/?_gl=1*1lwgnt1*_ga*OTY3MzQ5Mzk0LjE3NDEyMDc2NDA.*_ga_RKXFW6CM42*MTc0MTIwNzY0MC4xLjEuMTc0MTIwNzgxMS4yOS4wLjA.
"""



#include_path = '/usr/include/python3.10'
#include_path = '/Library/Frameworks/Python.framework/Versions/3.10/include/python3.10'
non_installed_packages = {}
include_path = None
found_head_file = 0
freetrace_path = ''
freetrace_path += 'FreeTrace'.join(re.split(r'FreeTrace', __file__)[:-1]) + 'FreeTrace'



if 'win' in platform and 'dar' not in platform:
    if '3.13' in sys.version:
        tf_version = 'tensorflow==2.17'
        python_version = "3.13"
    elif '3.12' in sys.version:
        tf_version = 'tensorflow==2.17'
        python_version = "3.12"
    elif '3.11' in sys.version:
        tf_version = 'tensorflow==2.17'
        python_version = "3.11"
    elif '3.10' in sys.version:
        tf_version = 'tensorflow==2.14'
        python_version = "3.10"
    else:
        sys.exit('***** python version 3.10/11/12/13 required for the compatibility with Tensorflow [No GPU use in windows] *****')

    print("***** FreeTrace includes the installation of below items. *****")
    with open(f"{freetrace_path}/requirements.txt", 'r') as f:
        lines = f.readlines()
        for line in lines:
            if f'tensorflow' in line:
                print(tf_version)
            else:
                pack = line.split("\n")[0]
                print(f'{pack}', end=' ')
    print("unzip clang python3-tk python3-dev python3-pip\n")
    print("If you don't want to continue, please stop the process.")
    time.sleep(5)
    print("Installing models... this takes minutes.")
    freetrace_path = freetrace_path.replace('\\', '/')
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])

    if python_version == "3.10":
        subprocess.run(['winget', 'install', 'Microsoft.Powershell'])
        subprocess.run(['pwsh.exe', '-Command', 'rm', '-Recurse', '-Force', f'\"{freetrace_path}/models\"'])
        subprocess.run(['pwsh.exe', '-Command', "$ProgressPreference=\'SilentlyContinue\'", ';', 
                        'iwr', '-Uri', "\"https://psilo.sorbonne-universite.fr/index.php/s/o8SZrWt4HePY8js/download/models_2_14.zip\"",
                        '-OutFile', f'{freetrace_path}/models_2_14.zip'])
        subprocess.run(['pwsh.exe', '-Command', 'Expand-Archive', '-Path', f'\"{freetrace_path}/models_2_14.zip\"', '-DestinationPath', f'\"{freetrace_path}/models\"'])
        subprocess.run(['pwsh.exe', '-Command', 'rm', f'\"{freetrace_path}/models_2_14.zip\"'])
    else:
        subprocess.run(['winget', 'install', 'Microsoft.Powershell'])
        subprocess.run(['pwsh.exe', '-Command', 'rm', '-Recurse', '-Force', f'\"{freetrace_path}/models\"'])
        subprocess.run(['pwsh.exe', '-Command', "$ProgressPreference=\'SilentlyContinue\'", ';', 
                        'iwr', '-Uri', "\"https://psilo.sorbonne-universite.fr/index.php/s/w9PrAQbxsNJrEFc/download/models_2_17.zip\"",
                        '-OutFile', f'{freetrace_path}/models_2_17.zip'])   
        subprocess.run(['pwsh.exe', '-Command', 'Expand-Archive', '-Path', f'\"{freetrace_path}/models_2_17.zip\"', '-DestinationPath', f'\"{freetrace_path}/models\"'])
        subprocess.run(['pwsh.exe', '-Command', 'rm', f'\"{freetrace_path}/models_2_17.zip\"'])

    if not os.path.exists(f'{freetrace_path}/models/theta_hat.npz') or not os.path.exists(f'{freetrace_path}/models/std_sets.npz'):
        print(f'***** Parmeters[theta_hat.npz, std_sets.npz] are not found for trajectory inference, please contact author for the pretrained models. *****\n')
        sys.exit()

    if os.path.exists(f'{freetrace_path}/requirements.txt'):
        with open(f'{freetrace_path}/requirements.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                package = line.strip().split('\n')[0]
                if 'tensorflow' in package:
                    package = tf_version
                try:
                    pid = subprocess.run([sys.executable, '-m', 'pip', 'install', package])
                    if pid.returncode != 0:
                        non_installed_packages[package] = pid.returncode
                except:
                    pass

    try:
        subprocess.run(['pwsh.exe', '-Command', f"{sys.executable}", f"{freetrace_path}/module/cython_build/cython_setup.py", 'build_ext', '--inplace'])
    except Exception as e:
        print(f'\n***** Compiling Error: {e} *****')
        pass

    if len(list(non_installed_packages.keys())) == 0:
        print(f'***** Pacakge installations finished succesfully. *****')
        print(f'***** Python veirsion: {python_version} *****')
        print('')
    else:
        for non_installed_pacakge in non_installed_packages.keys():
            print(f'***** Package [{non_installed_pacakge}] installation failed due to subprocess exit code:{non_installed_packages[non_installed_pacakge]}, please install it manually. *****')
        print('')



elif 'linux' in platform:
    if '3.13' in sys.version:
        tf_version = 'tensorflow[and-cuda]==2.17'
        python_version = "3.13" 
    elif '3.12' in sys.version:
        tf_version = 'tensorflow[and-cuda]==2.17'
        python_version = "3.12"
    elif '3.11' in sys.version:
        tf_version = 'tensorflow[and-cuda]==2.17'
        python_version = "3.11"
    elif '3.10' in sys.version:
        tf_version = 'tensorflow[and-cuda]==2.14.1'
        python_version = "3.10"
    else:
        sys.exit('***** python version 3.10/11/12/13 required for the compatibility with Tensorflow *****')

    print("***** FreeTrace needs Cuda. if Cuda is not installed, please visit [https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=24.04&target_type=deb_network] *****")
    print("***** FreeTrace includes the installation of below items. *****")
    with open(f"{freetrace_path}/requirements.txt", 'r') as f:
        lines = f.readlines()
        for line in lines:
            if f'tensorflow' in line:
                print(tf_version)
            else:
                pack = line.split("\n")[0]
                print(f'{pack}', end=' ')
    print("unzip clang python3-tk python3-dev python3-pip\n")
    print("If you don't want to continue, please stop the process.")
    time.sleep(5)

    print("\n***** Installtion starts *****")
    subprocess.run(['sudo', 'apt-get', 'update'])
    subprocess.run(['sudo', 'apt-get', 'install', 'unzip'])
    subprocess.run(['sudo', 'apt', 'install', 'clang'])
    subprocess.run(['sudo', 'apt', 'install', 'wget'])
    subprocess.run(['sudo', 'apt-get', 'install', 'python3-tk'])
    subprocess.run(['sudo', 'apt', 'install', 'python3-dev'])
    subprocess.run(['sudo', 'apt', 'install', 'python3-pip'])
    subprocess.run(['sudo', 'apt', 'install', 'python3-venv'])
    subprocess.run(['sudo', 'apt-get', 'install', 'libgl1'])
    subprocess.run(['sudo', 'apt-get', 'install', 'libgtk2.0-dev'])
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])

    if python_version == "3.10":
        subprocess.run(['rm', '-r', f'{freetrace_path}/models'])
        subprocess.run(['wget', 'https://psilo.sorbonne-universite.fr/index.php/s/o8SZrWt4HePY8js/download/models_2_14.zip', '-P' f'{freetrace_path}'])
        subprocess.run(['unzip', '-o', f'{freetrace_path}/models_2_14.zip', '-d', f'{freetrace_path}/models_2_14'])
        subprocess.run(['cp', '-r', f'{freetrace_path}/models_2_14', f'{freetrace_path}/models'])
        subprocess.run(['rm', '-r', f'{freetrace_path}/models_2_14'])
        subprocess.run(['rm', f'{freetrace_path}/models_2_14.zip'])
    else:
        subprocess.run(['rm', '-r', f'{freetrace_path}/models'])
        subprocess.run(['wget', 'https://psilo.sorbonne-universite.fr/index.php/s/w9PrAQbxsNJrEFc/download/models_2_17.zip', '-P' f'{freetrace_path}'])
        subprocess.run(['unzip', '-o', f'{freetrace_path}/models_2_17.zip', '-d', f'{freetrace_path}/models_2_17'])
        subprocess.run(['cp', '-r', f'{freetrace_path}/models_2_17', f'{freetrace_path}/models'])
        subprocess.run(['rm', '-r', f'{freetrace_path}/models_2_17'])
        subprocess.run(['rm', f'{freetrace_path}/models_2_17.zip'])
        
    for root, dirs, files in os.walk("/usr", topdown=False):
        for name in files:
            if 'Python.h' in name:
                include_path = f'{root}'
                found_head_file = 1

    if found_head_file == 0 :
        for root, dirs, files in os.walk("/Library", topdown=False):
            for name in files:
                if 'Python.h' in name:
                    include_path = f'{root}'
                    found_head_file = 1

    if include_path is None and found_head_file == 0:
        sys.exit(f'***** Please install python-dev to install modules, Python.h header file was not found. *****')
        
    if not os.path.exists(f'{freetrace_path}/models/theta_hat.npz') or not os.path.exists(f'{freetrace_path}/models/std_sets.npz'):
        print(f'***** Parmeters[theta_hat.npz, std_sets.npz] are not found for trajectory inference, please contact author for the pretrained models. *****\n')
        sys.exit()

    if os.path.exists(f'{freetrace_path}/requirements.txt'):
        with open(f'{freetrace_path}/requirements.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                package = line.strip().split('\n')[0]
                if 'tensorflow' in package:
                    package = tf_version
                try:
                    pid = subprocess.run([sys.executable, '-m', 'pip', 'install', package])
                    if pid.returncode != 0:
                        non_installed_packages[package] = pid.returncode
                except:
                    pass

    try:
        if python_version == "3.10":
            subprocess.run(['clang', '-Wno-unused-result', '-Wsign-compare', '-Wunreachable-code', '-fno-common', '-dynamic', '-DNDEBUG', '-g', '-fwrapv', '-O3', '-Wall', '-arch', 'arm64', '-arch', 'x86_64', '-g', '-fPIC', '-I', f'{include_path}',
                            '-c', f'{freetrace_path}/module/image_pad.c', '-o', f'{freetrace_path}/module/image_pad.o'])
            subprocess.run(['clang', '-shared', '-g', '-fwrapv', '-undefined', 'dynamic_lookup', '-arch', 'arm64', '-arch', 'x86_64',
                            '-g', f'{freetrace_path}/module/image_pad.o', '-o', f'{freetrace_path}/module/image_pad.so'])
            
            subprocess.run(['clang', '-Wno-unused-result', '-Wsign-compare', '-Wunreachable-code', '-fno-common', '-dynamic', '-DNDEBUG', '-g', '-fwrapv', '-O3', '-Wall', '-arch', 'arm64', '-arch', 'x86_64', '-g', '-fPIC', '-I', f'{include_path}',
                            '-c', f'{freetrace_path}/module/regression.c', '-o', f'{freetrace_path}/module/regression.o'])
            subprocess.run(['clang', '-shared', '-g', '-fwrapv', '-undefined', 'dynamic_lookup', '-arch', 'arm64', '-arch', 'x86_64',
                            '-g', f'{freetrace_path}/module/regression.o', '-o', f'{freetrace_path}/module/regression.so'])
            
            subprocess.run(['clang', '-Wno-unused-result', '-Wsign-compare', '-Wunreachable-code', '-fno-common', '-dynamic', '-DNDEBUG', '-g', '-fwrapv', '-O3', '-Wall', '-arch', 'arm64', '-arch', 'x86_64', '-g', '-fPIC', '-I', f'{include_path}',
                            '-c', f'{freetrace_path}/module/cost_function.c', '-o', f'{freetrace_path}/module/cost_function.o'])
            subprocess.run(['clang', '-shared', '-g', '-fwrapv', '-undefined', 'dynamic_lookup', '-arch', 'arm64', '-arch', 'x86_64',
                            '-g', f'{freetrace_path}/module/cost_function.o', '-o', f'{freetrace_path}/module/cost_function.so'])
            
        else:
            subprocess.run(['clang', '-Wno-unused-result', '-Wsign-compare', '-Wunreachable-code', '-fno-common', '-dynamic', '-DNDEBUG', '-g', '-fwrapv', '-O3', '-Wall', '-g', '-fPIC', '-I', f'{include_path}',
                            '-c', f'{freetrace_path}/module/image_pad.c', '-o', f'{freetrace_path}/module/image_pad.o'])
            subprocess.run(['clang', '-shared', '-g', '-fwrapv', '-undefined', 'dynamic_lookup',
                            '-g', f'{freetrace_path}/module/image_pad.o', '-o', f'{freetrace_path}/module/image_pad.so'])
            
            subprocess.run(['clang', '-Wno-unused-result', '-Wsign-compare', '-Wunreachable-code', '-fno-common', '-dynamic', '-DNDEBUG', '-g', '-fwrapv', '-O3', '-Wall', '-g', '-fPIC', '-I', f'{include_path}',
                            '-c', f'{freetrace_path}/module/regression.c', '-o', f'{freetrace_path}/module/regression.o'])
            subprocess.run(['clang', '-shared', '-g', '-fwrapv', '-undefined', 'dynamic_lookup',
                            '-g', f'{freetrace_path}/module/regression.o', '-o', f'{freetrace_path}/module/regression.so'])

            subprocess.run(['clang', '-Wno-unused-result', '-Wsign-compare', '-Wunreachable-code', '-fno-common', '-dynamic', '-DNDEBUG', '-g', '-fwrapv', '-O3', '-Wall', '-g', '-fPIC', '-I', f'{include_path}',
                            '-c', f'{freetrace_path}/module/cost_function.c', '-o', f'{freetrace_path}/module/cost_function.o'])
            subprocess.run(['clang', '-shared', '-g', '-fwrapv', '-undefined', 'dynamic_lookup',
                            '-g', f'{freetrace_path}/module/cost_function.o', '-o', f'{freetrace_path}/module/cost_function.so'])    

        subprocess.run(['rm', f'{freetrace_path}/module/image_pad.o', f'{freetrace_path}/module/regression.o', f'{freetrace_path}/module/cost_function.o'])
        if os.path.exists(f'{freetrace_path}/module/image_pad.so') and os.path.exists(f'{freetrace_path}/module/regression.so') and os.path.exists(f'{freetrace_path}/module/cost_function.so'):
            print('')
            print(f'***** module compiling finished successfully. *****')
    except Exception as e:
        print(f'\n***** Compiling Error: {e} *****')
        pass

    if len(list(non_installed_packages.keys())) == 0:
        print(f'***** Pacakge installations finished succesfully. *****')
        print(f'***** Python veirsion: {python_version} *****')
        print('')
    else:
        for non_installed_pacakge in non_installed_packages.keys():
            print(f'***** Package [{non_installed_pacakge}] installation failed due to subprocess exit code:{non_installed_packages[non_installed_pacakge]}, please install it manually. *****')
        print('')



elif 'darwin' in platform:
    if '3.13' in sys.version:
        tf_version = 'tensorflow==2.17'
        python_version = "3.13"
    elif '3.12' in sys.version:
        tf_version = 'tensorflow==2.17'
        python_version = "3.12"
    elif '3.11' in sys.version:
        tf_version = 'tensorflow==2.17'
        python_version = "3.11"
    elif '3.10' in sys.version:
        tf_version = 'tensorflow==2.14'
        python_version = "3.10"
    else:
        sys.exit('***** python version 3.10/11/12/13 required for the compatibility with Tensorflow [No GPU use in windows] *****')

    print("***** FreeTrace includes the installation of below items. *****")
    with open(f"{freetrace_path}/requirements.txt", 'r') as f:
        lines = f.readlines()
        for line in lines:
            if f'tensorflow' in line:
                print(tf_version)
            else:
                pack = line.split("\n")[0]
                print(f'{pack}', end=' ')
    print("unzip clang python3-tk python3-dev python3-pip\n")
    print("If you don't want to continue, please stop the process.")
    time.sleep(5)
    print("Installing models... this takes minutes.")
    freetrace_path = freetrace_path.replace('\\', '/')
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])

    
    if python_version == "3.10":
        subprocess.run(['rm', '-r', '-f', f"{freetrace_path}/models"])
        subprocess.run(['curl', '-O', '-s', 'https://psilo.sorbonne-universite.fr/index.php/s/o8SZrWt4HePY8js/download/models_2_14.zip'])
        subprocess.run(['unzip', f"{os.getcwd()}/models_2_14.zip", "-d", f"{freetrace_path}/models"])
        subprocess.run(['rm', f"{os.getcwd()}/models_2_14.zip"])
    else:
        subprocess.run(['rm', '-r', '-f', f"{freetrace_path}/models"])
        subprocess.run(['curl', '-O', '-s', 'https://psilo.sorbonne-universite.fr/index.php/s/w9PrAQbxsNJrEFc/download/models_2_17.zip'])
        subprocess.run(['unzip', f"{os.getcwd()}/models_2_17.zip", "-d", f"{freetrace_path}/models"])
        subprocess.run(['rm', f"{os.getcwd()}/models_2_17.zip"])
    

    if not os.path.exists(f'{freetrace_path}/models/theta_hat.npz') or not os.path.exists(f'{freetrace_path}/models/std_sets.npz'):
        print(f'***** Parmeters[theta_hat.npz, std_sets.npz] are not found for trajectory inference, please contact author for the pretrained models. *****\n')
        sys.exit()

    if os.path.exists(f'{freetrace_path}/requirements.txt'):
        with open(f'{freetrace_path}/requirements.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                package = line.strip().split('\n')[0]
                if 'tensorflow' in package:
                    package = tf_version
                try:
                    pid = subprocess.run([sys.executable, '-m', 'pip', 'install', package])
                    if pid.returncode != 0:
                        non_installed_packages[package] = pid.returncode
                except:
                    pass

    try:
        subprocess.run([f"{sys.executable}", f"{freetrace_path}/module/cython_build/cython_setup.py", 'build_ext', '--inplace'])
    except Exception as e:
        print(f'\n***** Compiling Error: {e} *****')
        pass

    if len(list(non_installed_packages.keys())) == 0:
        print(f'***** Pacakge installations finished succesfully. *****')
        print(f'***** Python veirsion: {python_version} *****')
        print('')
    else:
        for non_installed_pacakge in non_installed_packages.keys():
            print(f'***** Package [{non_installed_pacakge}] installation failed due to subprocess exit code:{non_installed_packages[non_installed_pacakge]}, please install it manually. *****')
        print('')
    
    if python_version == '3.10' or python_version == '3.11' or python_version == '3.12':
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'tensorflow-metal'])
    else:
        print(f"Current python version: {sys.version}")
        print(f"Tensorflow for MacOS is stable for python 3.10 / 3.11 / 3.12,  To utilise tensorflow-metal, please change the python version.")
        # python3 -m pip install tensorflow-metal # Not available for python3.13 12/08/2025



else:
    sys.exit("No supported OS.\n")

