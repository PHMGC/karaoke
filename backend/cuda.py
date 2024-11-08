import os
import re
import sys
try:
    import requests
    import torch
except ModuleNotFoundError as e:
    print("Make sure you installed all the backend dependencies before running this script")
    sys.exit()


def check_sys_cuda_version():
    try:
        output = os.popen('nvidia-smi').read()
        if "CUDA Version" in output:
            cuda_version_match = re.search(r'CUDA Version: (\d+\.\d+)', output)
            if cuda_version_match:
                return float(cuda_version_match.group(1))

    except Exception as e:
        print(e)

    return


def check_available_pytorch_cuda_version(version):
    print("Checking available PyTorch versions for your CUDA version")
    for pos_version in range(version, 0, -1):
        url = f"https://download.pytorch.org/whl/cu{pos_version}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return url
        except requests.exceptions.RequestException:
            pass
    return


if __name__ == "__main__":
    if not torch.cuda.is_available():
        cuda_version = check_sys_cuda_version()
        if cuda_version:
            print(f"CUDA Version: {cuda_version}")
            ver = str(cuda_version).replace('.', '')
            int_ver = int(ver)
            url = check_available_pytorch_cuda_version(int_ver)
            if url:
                print(f"Found: {url}")
                os.system(
                    f"pip install --force-reinstall torch torchvision torchaudio --index-url {url}")
            else:
                print(f"Couldn't find a PyTorchCUDA version compatible for your CUDA version, please install it manually on https://pytorch.org/")
        else:
            print(f"Couldn't find your CUDA version, please check if your system is compatible using the command nvidia-smi on console, and install it manually on https://pytorch.org/")
    else:
        print("CUDA is already installed in your system")
