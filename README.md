# Fetchdeb

Fetchdeb is a simple command-line tool for downloading Debian package files (`.deb`) and their dependencies directly from the official Debian repositories. It is useful for offline installations or when you need to collect `.deb` files for specific packages.

## Features
- Downloads `.deb` files for specified packages from the Debian repository
- Optionally downloads all required dependencies
- Optionally downloads recommended packages
- Works on Windows (requires Python)

## Requirements
- Python 3.x
- `requests` Python package (automatically installed if missing)

## Usage

There are two ways of using this tool. Either run it by referencing the .bat file, or add the .bat file to the PATH variable for easier use.

### Running by reference

1. Open a command prompt in the directory you want to download to.
2. Run the following command:

    ```sh
    <path to fetchdeb.bat> <package1> <package2> ...
    ```

3. The script will prompt you to download dependencies and recommend packages. Answer `y` or `n` as desired.
4. Downloaded `.deb` files will be saved in the current working directory.

### Adding fetchdeb.bat to the PATH

1. Locate the folder where fetchdeb.bat is saved (e.g., `C:\Tools\Custom tools\Fetchdeb`).
2. Press `Win + S`, type `environment variables`, and select **Edit the system environment variables**.
3. In the System Properties window, click **Environment Variables...**.
4. Under **System variables**, find and select the `Path` variable, then click **Edit...**.
5. Click **New** and enter the path to the folder containing `fetchdeb.bat`.
6. Click **OK** to close all windows.
7. Open a new command prompt and type `fetchdeb` to verify it works.

Now you can run fetchdeb easily

### Running from PATH

1. Open a command prompt in the directory you want to download to.
2. Run the following command:

    ```sh
    fetchdeb <package1> <package2> ...
    ```

3. The script will prompt you to download dependencies and recommend packages. Answer `y` or `n` as desired.
4. Downloaded `.deb` files will be saved in the current working directory.

#### Example

```
C:\Tools\Fetchdeb vim curl
```
or running from PATH
```
fetchdeb vim curl
```

This will download the `.deb` files for `vim` and `curl`, along with their dependencies and recommended packages if you choose to include them.

## Notes
- The script fetches package information from the Debian Bookworm (stable) main repository for amd64 architecture.
- You can run the tool from any directory; downloaded files will appear in your current directory.
- If a package is not found, it will be listed in the output.
- The script will not re-download files that already exist in the output directory.

## License
This tool is provided as-is, without warranty. Use at your own risk.
