# Foreword

This is just supposed to be a quick write-up of how i've gotten SADX and LiveSplit to work, including the Autosplitting feature.  
While it worked for me, we all know tech can behave funny sometimes so if this method doesn't work for you feel free to try the other Guides from this repo!

If you notice any mistakes or outdated info in this Guide, or have any questions, don't hesitate to DM [nanami.tv](https://discord.com/users/599588626698993699) or Ping me on the [SADX speedrunning server](https://discord.gg/NCUdvEwWMA)


# Installation

## Prerequisites

- **Lutris** - If you don't know where to get Lutris refer to their own [install guide](https://lutris.net/downloads)

- **wine-ge-8-26-x86_64** - This is the version i run and confirmed it working with, other wine/proton versions might work but uncomfirmed

- **The most recent LiveSplit version** - [Download the newest release](https://github.com/LiveSplit/LiveSplit/releases)

- **SADX Coupon V7** - You can download it from the #resources channel in the [SADX speedrunning server](https://discord.gg/NCUdvEwWMA)

## Preparing the game

1. Extract the SADX Coupon V7.zip to where you want the game to be (I'll be using `/home/USER/Games/sadx/` in this guide)

2. Open Lutris and click the `+` icon in the top-left corner

![Imgur](https://i.imgur.com/JiBaOKW.png)

3. Click on `Add locally installed game`

4. Fill out the different fields as shown in the screenshots

![Imgur](https://imgur.com/HcQ4oZW.png)

![Imgur](https://imgur.com/RsMCbb3.png)

![Imgur](https://imgur.com/ety3hLG.png)

> Don't change anything in `System options`

5. Start the game/ModManager through Lutris once (select the game and click `Play` on the bottom-left)
> If it asks you to install any redist like .NET etc click `No` - It will just exit.

6. Copy your `SONICADVENTUREDX` game folder into `/home/USER/Games/sadx/prefix/drive_c/Program Files/`

7. Right-click your game in Lutris and click `Configure` and go into `Game options`

8. Change the `Executable` and `Working directory` as shown in the screenshot

![Imgur](https://imgur.com/pNO3oWE.png)

9. In your Lutris window on the bottom-left click on the Arrow next to the wineglass and open `Winetricks`

![Imgur](https://imgur.com/HO4vbAh.png)

10. In the Winetricks window click `Select the default wineprefix` and `OK`
- Click `Install a Windows DLL or component`
- In the list that opens select the following:
    - `d3dx9`
    - `quartz`
    - `dotnet7`
    - `dotnet8`
    - `dotnetdesktop7`
    - `dotnetdesktop8`
- Click `OK` and wait for the window to re-open

11. In the same menu where you opened Winetricks open `Wine configuration`

12. In the Wine configuration window click on `Libraries` and follow the screenshots below:

![Imgur](https://imgur.com/eGrN5IS.png)

![Imgur](https://imgur.com/aWsSU4O.png)

![Imgur](https://imgur.com/MB3eZJP.png)

![Imgur](https://imgur.com/l3ZBLam.png)

13. Start the game/ModManager through Lutris again, it should work now.
> If it prompts you to update the ModManager **DO NOT** update!

14. Configure your ModManager according to my screenshots below:

![Imgur](https://imgur.com/eowiAUI.png)

![Imgur](https://imgur.com/7NgqmXX.png)

> Now try to start the game by clicking `Save & Play` in the Mod Manager, it should start successfully!

## LiveSplit setup

1. Go into `/home/USER/Games/sadx/prefix/drive_c/Program Files/SONICADVENTUREDX/TOOLS/LiveSplit/` and delete every file inside that folder

2. Extract your [most recent release](https://github.com/LiveSplit/LiveSplit/releases) of LiveSplit into that folder

3. In Lutris open the same menu that you opened both Winetricks and Wine configuration earlier and click on `Run EXE inside Wine prefix`

4. Navigate to `/home/USER/Games/sadx/prefix/drive_c/Program Files/SONICADVENTUREDX/TOOLS/LiveSplit/` and open `LiveSplit.exe`

5. LiveSplit should now open and be ready to be set-up normally
> To open LiveSplit in the future repeat steps 3. & 4.

## Conclusion
This should be all the setup you need! If you need any additional help dont hesitate to contact me through the methods mentioned at the top! Happy running!😁
