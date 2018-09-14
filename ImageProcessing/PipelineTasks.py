{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Pipeline Tasks\n",
    "\n",
    "<br>Owner: **Alex Drlica-Wagner** ([@kadrlica](https://github.com/LSSTScienceCollaborations/StackClub/issues/new?body=@kadrlica))\n",
    "<br>Last Verified to Run: **2018-08-10**\n",
    "<br>Verified Stack Release: **v16.0**\n",
    "\n",
    "## Learning Objectives:\n",
    "\n",
    "This notebook seeks to teach users how to unpack a pipeline tasks. As an example, we focus on `processCcd.py`, with the goal of diving into the configuration, interface, and structure of pipeline tasks. This notebook is a digression from Justin Myles script that demonstrates how to run a series of pipeline tasks from the command line to rerun HSC data processing [link].\n",
    "\n",
    "After working through this tutorial you should be able to:\n",
    "\n",
    "* Find the source code for a pipeline task\n",
    "* Configure (and investigate the configuration) of pipeline tasks\n",
    "* Investigate and run those tasks in python\n",
    "\n",
    "## Logistics\n",
    "This notebook is intended to be runnable on `lsst-lspdev.ncsa.illinois.edu` from a local git clone of https://github.com/LSSTScienceCollaborations/StackClub."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import pydoc"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Command Line Processing\n",
    "\n",
    "In this first step we perform command line processing of images following the getting started tutorials [here](https://pipelines.lsst.io/getting-started/data-setup.html#) and [here](https://pipelines.lsst.io/getting-started/processccd.html). We are specifically interested in digging into the following line:\n",
    "\n",
    "```\n",
    "processCcd.py $DATADIR --rerun processCcdOutputs --id\n",
    "```"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "We start by tracking down the location of the `processCcd.py` shell script"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "!(which processCcd.py)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "This is the proverbial \"end of the thread\". Our goal is to pull on this thread to unravel the python/C++ functions that are being called under the hood. We start by taking a peak in this script"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "!cat $(which processCcd.py)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Ok, this hasn't gotten us very far, but after getting through the stock header, we now have the next link in our chain:\n",
    "```\n",
    "from lsst.pipe.tasks.processCcd import ProcessCcdTask\n",
    "```\n",
    "\n",
    "There are two ways we can proceed from here. One is to [Google](http://lmgtfy.com/?q=lsst.pipe.tasks.processCcd) `lsst.pipe.tasks.processCcd`, which will take us to this [doxygen page](http://doxygen.lsst.codes/stack/doxygen/x_masterDoxyDoc/classlsst_1_1pipe_1_1tasks_1_1process_ccd_1_1_process_ccd_task.html) and/or the soure code on [GitHub](https://github.com/lsst/pipe_tasks/blob/master/python/lsst/pipe/tasks/processCcd.py). \n",
    "\n",
    "The second approach is to do the import the class oursleves and try to investigate it interactively.\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import lsst.pipe.tasks.processCcd\n",
    "from lsst.pipe.tasks.processCcd import ProcessCcdTask, ProcessCcdConfig"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "We can get to the source code for these classes directly using the [`stackclub` toolkit module](https://stackclub.readthedocs.io/), as shown in the [FindingDocs.ipynb](https://github.com/LSSTScienceCollaborations/StackClub/blob/master/GettingStarted/FindingDocs.ipynb)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from stackclub import where_is\n",
    "where_is(ProcessCcdConfig)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Next we can create an instance of the `ProcessCcdConfig` and try calling the `help` method (commented out for brevity). What we are really interested in are the \"Data descriptors\", which we can print directly after capturing the documentation output by `help`."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "config = ProcessCcdConfig()\n",
    "#help(config)\n",
    "helplist = pydoc.render_doc(config).split('\\n')\n",
    "print('\\n'.join(helplist[18:47]))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "The first step is to try to get at the documentation through the `help` function (commented out below for brevity). We can find "
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "The `ProcessCcdConfig` object contains of both raw configurables like `doCalibrate` and other configs, like `isr`. To investigate one of these in more detail, we can import it and query it's \"Data descriptors\".\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from lsst.ip.isr.isrTask import IsrTask, IsrTaskConfig\n",
    "print('\\n'.join(pydoc.render_doc(IsrTaskConfig).split('\\n')[16:40]) + '...')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "These configurationas are pretty self-explanitory, but say that we really want to understand what `doFringe` is doing. Inorder to get that information we need to go to the source code."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "where_is(IsrTaskConfig)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "We can then search this file for `doFringe` and we find [several lines](https://github.com/lsst/ip_isr/blob/cc4efb7d763d3663c9e989339505df9654f23fd9/python/lsst/ip/isr/isrTask.py#L597-L598) that look like this:\n",
    "\n",
    "        if self.config.doFringe and not self.config.fringeAfterFlat:\n",
    "            self.fringe.run(ccdExposure, **fringes.getDict())\n",
    "            \n",
    "If we want to go deeper to see what `fringe.run` does, we can repeat the above process"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "isr_task = IsrTask()\n",
    "print(isr_task.fringe)\n",
    "import  lsst.ip.isr.fringe\n",
    "where_is(lsst.ip.isr.fringe.FringeTask)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "We finally make our way to the source code for [FringeTask.run](https://github.com/lsst/ip_isr/blob/cc4efb7d763d3663c9e989339505df9654f23fd9/python/lsst/ip/isr/fringe.py#L104), which gives us details on the fringe subtraction."
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "LSST",
   "language": "python",
   "name": "lsst"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.2"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
