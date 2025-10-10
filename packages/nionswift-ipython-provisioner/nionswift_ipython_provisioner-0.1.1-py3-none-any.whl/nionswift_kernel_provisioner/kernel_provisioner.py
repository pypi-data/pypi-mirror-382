import typing
import os
import sys
from importlib import resources
import json

from jupyter_client.connect import KernelConnectionInfo
from jupyter_client import kernelspec
from jupyter_client.provisioning import provisioner_base
from jupyter_core.paths import jupyter_runtime_dir


CONNECTION_FILE_NAME = "nionswift-ipython-kernel.json"
SWIFT_KERNEL_NAME = "nion_swift_kernel"


class SwiftProvisioner(provisioner_base.KernelProvisionerBase): # type: ignore
    """Kernel provision for Nion Swift.

    See https://jupyter-client.readthedocs.io/en/stable/provisioning.html#kernel-provisioning for details about this.
    Essentially this is a wrapper around the jupyter kernel start mechanism that allows customizing how a kernel is
    launched. We don't actually launch a kernel here but just connect to the Nion Swift ipython kernel.
    """

    @staticmethod
    def install_swift_kernel_spec() -> None:
        """Install the swift kernel spec.

        Using 'sys.prefix' as the prefix in the installtion routine installs the current virtualenv or conda
        environment if the current python is running in such. Like this we don't disrupt any other python
        installtions.
        """
        kernel_source_dir =  resources.files("nionswift_kernel_provisioner").joinpath("resources/nion_swift_kernel")
        kernelspec.install_kernel_spec(str(kernel_source_dir), kernel_name=SWIFT_KERNEL_NAME, prefix=sys.prefix)

    @property
    def _connection_file(self) -> str:
        """
        We use our custom connection file name so that we can find the swift kernel from any process.
        """
        return os.path.join(jupyter_runtime_dir(), CONNECTION_FILE_NAME)

    @property
    def has_process(self) -> bool:
        """
        This is used by jupyter to check if the kernel process is still alive. We cannot really check if Swift is running
        here, but we can check if the connection file exists. During a normal shutdown of Swift's ipython kernel the
        connection file created by it gets deleted, so at least to a certain extent we can detect whether it is running
        or not.
        """
        return os.path.exists(self._connection_file)

    async def poll(self) -> typing.Optional[int]:
        return None

    async def wait(self) -> typing.Optional[int]:
        return None

    async def send_signal(self, signum: int) -> None:
        return None

    async def kill(self, restart: bool = False) -> None:
        return None

    async def terminate(self, restart: bool = False) -> None:
        return None

    async def launch_kernel(self, cmd: typing.List[str], **kwargs: typing.Any) -> KernelConnectionInfo:
        """
        Normally this function would start an ipython kernel for jupyter to connect to and return the information
        about how to connect to it. Since the swift kernel is already running we simply load the connection info
        and return it.
        """
        with open(self._connection_file) as f:
            connection_info = json.load(f)
            # "key" needs to be a bytes object, otherwise jupyter will complain about non-matching kernel info
            if 'key' in connection_info:
                connection_info['key'] = connection_info['key'].encode()
        return typing.cast(KernelConnectionInfo, connection_info)

    async def cleanup(self, restart: bool = False) -> None:
        return None

    async def pre_launch(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        # Jupyter looks for a key 'cmd' in the return value of this function. Not providing it makes the kernel start
        # procedure crash, so just put a dummy entry in here.
        kwargs = kwargs.copy()
        kwargs["cmd"] = ""
        return kwargs

# For the jupyter kernel provisioner to find our kernel, we need to insert the kernel spec file into the
# correct location. Check if this has already happened and if not, install it here.
exisiting_kernels = kernelspec.find_kernel_specs()
if not SWIFT_KERNEL_NAME in exisiting_kernels:
    SwiftProvisioner.install_swift_kernel_spec()
