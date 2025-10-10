nionswift-ipython-provisioner
=============================

This is an `ipython kernel provisioner <https://jupyter-client.readthedocs.io/en/latest/provisioning.html>`_ for
``nionswift-ipython-kernel``.
It is required for connecting a jupyter notebook to ipython kernel running in Nion Swift, since there is no "--exisiting"
option for notebooks.

Simply install this package in the environment you want to use to run the jupyter notebook and select "Nion Swift" as
the kernel for the notebook.
This requires that Nion Swift is running and that ``nionswift-ipython-kernel`` is installed in the environment used to
run Nion Swift.

**Important Note:**
You need to run ``python -c "from nionswift_kernel_provisioner import kernel_provisioner"`` from within the environment
you installed this package in. This only needs to be done once per environment, not every time you want to start
a jupyter notebook.

The reason for this is that we need to write the kernel specs file out to disk, so that jupyter can find it. This can
only happen *after* the installation, but pip is lacking the ability to implement post-installation hooks, so for now
this needs to be done manually. See also this issue for a discussion on this topic: https://github.com/pypa/packaging-problems/issues/64
