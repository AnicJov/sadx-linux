# Preface
So there are for sure a million ways of going about this but I'm sharing this method because it works well[^1] for me and it's relatively simple, using only GUI tools and not needing to open the terminal once. So feel free to follow along or use this as a starting point for you own setup.

Before you proceed I recommend setting up your distro for gaming if you haven't already, installing all required drivers and dependecies. This process will depend on your distro as well as your hardware so I suggest searching up a guide specific to your needs.

[This ArchWiki article](https://wiki.archlinux.org/title/Gaming) might help you. It's quite in-depth but it should cover everything you'd ever need to configure to get better performance.

[^1]: Works well most of the time.

Also, if some part of this guide is outdated, or you're facing some issues, feel free to contact me on Discord [@\_anic](https://discord.com/users/147104361032450048) either in DMs or in the [SADX speedrunning server](https://discord.gg/FA5QHhTvKs).


# Process

## Lutris install
We will use Lutris for managing games and their Wine prefixes. Install it in the usual way you install packages on your distro, either using a graphical package manager or the terminal.
If you're unsure how to do this refer to [Lutris' install instructions](https://lutris.net/downloads).

![image](https://user-images.githubusercontent.com/25593018/250271774-0af431ca-e080-44d0-a47a-16c4ae16d1b0.png)


## Game install

First, download the [sadx-coupon.yml](https://gist.githubusercontent.com/AnicJov/be2a498650ed22feb4c82db70f3156be/raw/761146114613f20bc68e59e035600b7b0d5614f7/sadx-coupon.yml) file by right clicking on the link and selecting `Save Link As...`, or get it from below this guide. This file is the install script.



Now open up Lutris.

Click on the `+` in the top left corner to add a new game, and select the `Install from a local install script` option.

![image](https://user-images.githubusercontent.com/25593018/250272691-be70edd8-2e89-4987-be8f-80a68109ffd4.png)


Click on `Browse...` and find the [sadx-coupon.yml](https://gist.githubusercontent.com/AnicJov/be2a498650ed22feb4c82db70f3156be/raw/761146114613f20bc68e59e035600b7b0d5614f7/sadx-coupon.yml) file you just downloaded, then click `Install`.

![image](https://user-images.githubusercontent.com/25593018/250272744-75d74bcd-edf1-4df0-9a86-6ec815631b0e.png)

Click on `Install`, then `Continue`, and `Install` one more time.
The installer should now download the SADX coupon and LiveSplit, set up the wine prefix and install everything the game needs in it, and extract the coupon and LiveSplit.

![image](https://user-images.githubusercontent.com/25593018/250272786-98ed6f9a-d34e-4d97-852c-dbc219dcb832.png)

If everything completes the game should be installed and ready to run. You can press `Launch` to start it.


## Mod Manager setup

When you launch the game the Mod Manager will start up.

It will first ask you for the language, so pick your preferred one and click `OK`.

![image](https://gist.github.com/user-attachments/assets/91c3d504-1dc3-4e5f-bbda-200a497bb08f)

Then it will ask you to download 7-zip, click on `Yes`.

![image](https://gist.github.com/user-attachments/assets/c21cd6ff-3ac2-4412-8f12-d55a60baa19e)

You will then be greeted with the welcome screen, click on `OK`.

![image](https://gist.github.com/user-attachments/assets/025197cb-3d2c-4f8b-8fe9-1dc6ca8b1471)

If there are any updates available, I suggest you get them installed. Click on `Download` if you get such prompts.

![image](https://gist.github.com/user-attachments/assets/390a6232-aced-41b9-a492-3f9d0cbb0607)

The Mod Manager will restart and now you should be looking at the main window. The first launch is now done and you won't have to go through this process again unless there are new updates that become available.

![image](https://gist.github.com/user-attachments/assets/ce04e2d2-2a22-43ef-bf85-2c899b06b83e)

Now you can go and configure the game through the Mod Manager to your liking.

From my testing I have configured my game for best performance so I suggest copying my settings as a starting point and then you can do your own experimentation and find out what works best for you. My settings are shown below.

![image](https://gist.github.com/user-attachments/assets/e65af597-03d7-4b9e-8431-e0ea87e2bb83)
![image](https://gist.github.com/user-attachments/assets/9b2843b0-f0ee-4854-b10d-44dface43d9b)
![image](https://gist.github.com/user-attachments/assets/3d57f91d-a018-4870-9cd5-369ed13356da)
![image](https://gist.github.com/user-attachments/assets/a4161baa-7bff-4127-983c-4ada49c07445)
![image](https://gist.github.com/user-attachments/assets/633bc9c9-63d0-44c4-ae06-f2ba2c8518ba)
![image](https://gist.github.com/user-attachments/assets/b3cba1eb-1c68-4212-84bc-18cf927608a2)
![image](https://gist.github.com/user-attachments/assets/d303cff7-9ebf-4ec6-a579-ab329948b1fd)
![image](https://gist.github.com/user-attachments/assets/35986bd0-dd98-463f-8736-d8c653ff8092)
![image](https://gist.github.com/user-attachments/assets/4509ab37-21e3-4e0b-b9fb-3fcab8a636b5)

> NOTE:
>   * Fullscreen without the `Borderless` option check doesn't seem to work[^2].
>   * `Enable D3D8to9` should always be checked on because it offers better performance, especially on Wine[^3].
>   * The Vertex Color Fixes, Material Color Fixes should always be disabled, from my experience they cause lag especially on stages like Sky Deck.
>   * Frame Limit mods don't really work on Linux, which shouldn't matter since the game runs at 60fps either way and we're timing IGT.
>   * The FMV cutscenes don't work on some systems which is a bummer but doesn't impact the speedrun in any way. You can still skip them by pressing the start button as you would normally.

[^2]: From what I know, on Linux systems running X display server there is no such thing as exclusive fullscreen so there would be no difference either way if this worked or not.
[^3]: Due to DXVK being used instead of Wine's slower D3D8 implementation.

Now you can click on `Save & Play` and the game should start up. That concludes the game setup.


## LiveSplit setup

For the LiveSplit auto splitter to work you must run LiveSplit with the same wine version, under the same wine prefix as the game. You can do this very easily through Lutris as shown below. You will be running LiveSplit this way every time.

Select the game, click on the up arrow next to the wine glass, and select `Run EXE inside Wine prefix`.

![image](https://user-images.githubusercontent.com/25593018/250273459-d6add465-755c-4965-8011-f2b6321a4f66.png)

Browse to `drive_c -> SONICADVENTUREDX -> TOOLS -> LiveSplit` and select `LiveSplit.exe`.

![image](https://user-images.githubusercontent.com/25593018/250273528-d99566c2-37b0-4020-ab24-423c221b1835.png)

LiveSplit should start up and you can proceed to configure it as you wish, the process is roughly the same as on Windows.

If you're having trouble give [this video guide](https://youtu.be/EzHKglGysik?si=5B1e_-gIeGiMUClO&t=110) a watch, or scream for help in the [SADX speedrunning Discord server](https://discord.gg/FA5QHhTvKs).

# Conclusion

And that's it! You should now be good to play and speedrun the game. Happy running! 🐧
