## OBS

This folder regroup scripts to make package using [OpenBuildService](https://build.opensuse.org/project/show/network:retroshare)

### Make your own OBS Fork Project

You needs an [OBS](https://build.opensuse.org/) account.
You can make one using Sign Up link.

Once logged, go to your "Home Project" "Overview".
In "Packages" frame, click on "Branch Existing Package".
Then choose:

    Original project name = network:retroshare
    Original package name = branch you want to build \(Some required retroshare-common-unstable\)
    Branch package name = the name of your branch. Let it empty will take original name.

Or you can make your own blank package. You only need to put in it corresponding _service file and made TarBall.

Now your packages defined, you have to select for which distribution you want to build.
For that go to your "Home Project" "Repositories".
Click on "Add from a Distribution" to get the available list.
Select the ones you want.
You will see them in right of "Overview" page with their results.

### Prepare your TarBall

As OBS's VM are not connected to Internet, you have to provide a TarBall (tar.gz file) of your project to build it.
This file \(RetroShare.tar.gz\) need to be uploaded to your package.
The script \(build_scripts/OBS/prepare_source_tarball.sh\) in git repository is here to create it.

You need first to have a clone copy on your local computer:

    git clone https://github.com/RetroShare/RetroShare.git RetroShare

And initialized OBS sub-module:

    git -C ./RetroShare/ submodule update --init build_scripts/OBS

Then call prepare script

    ./RetroShare/build_scripts/OBS/prepare_source_tarball.sh

In your OBS "Home Project" "Overview", you can now upload this RetroShare.tar.gz file.
The build start directly after.
