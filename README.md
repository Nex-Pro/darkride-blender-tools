# Tivoli Blender Tools

## Download

### You can find the latest releases here:

https://git.tivolicloud.com/tivolicloud/blender-tools/-/releases

### And the changelog here:

https://docs.tivolicloud.com/blender-tools/changelog

## Installation

No compiled releases exist yet so you have to do it manually.

-   ```bash
    python download_libs.py
    ```

-   Then load the repo dir as addon in Blender using a symbolic link.

## Blender compatibility

The add-on targets Blender 4.2 and newer, including Blender 5.x. The glTF
export features require Blender's glTF 2.0 importer/exporter add-on to be
installed and enabled.

## Developing

I recommend you use this extension for developing on VSCode:
https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development
