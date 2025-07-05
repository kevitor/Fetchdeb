# fetchdeb.py
import os
import sys
import subprocess

import gzip
import io

# Import or install 'request' dependency
try:
	import requests
except ImportError:
	import subprocess
	import sys
	print("'requests' module not found. Installing...")
	subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
	import requests

# Everything will be installed from deb.debian.org
DEBIAN_URL = "http://deb.debian.org/debian/"
# The Packages.gz file is the total list of pakages with their download path, dependencies, etc.
PACKAGES_GZ_URL = DEBIAN_URL + "dists/bookworm/main/binary-amd64/Packages.gz"
OUTPUT_DIR = os.getcwd()

DOWNLOAD_DEPENDENCIES = False
DOWNLOAD_SUGGESTED = False

def get_filenames(packages_list, target_packages):
	# Get the package paths from the list
	filenames = []
	current_pkg = None
	current_filename = None

	# Remove duplicates
	target_packages = list(set(target_packages))

	not_found = target_packages

	# Iterate through the packages list
	for line in packages_list.splitlines():
		if line.startswith("Package:"):
			current_pkg = line.split(":", 1)[1].strip()
			current_filename = None
		elif line.startswith("Filename:"):
			if current_pkg in target_packages:
				current_filename = line.split(":", 1)[1].strip()
				filenames.append(current_filename)
				not_found.remove(current_pkg)
	
	# If not all packages were found
	if len(filenames) < len(target_packages):
		print(f"get_filenames returned only {len(filenames)} out of {len(target_packages)} filenames.")
		print(f"Packages not found: {not_found}")

	return filenames

# Gets the dependencies for the target packages
def get_dependencies(packages_list, target_packages, excluded_packages = []):
	dependencies = []
	current_depends = []
	current_pkg = None

	for line in packages_list.splitlines():
		if line.startswith("Package:"):
			current_pkg = line.split(":", 1)[1].strip()
			current_depends = []
		elif line.startswith("Depends:"):
			if current_pkg in target_packages:
				current_depends = line.split(":", 1)[1].strip().split(", ")
				# Remove alternatives
				current_depends = [dependency.split(" | ")[0] for dependency in current_depends]
				# Remove version specifier
				current_depends = [dependency.split(" (")[0].strip() for dependency in current_depends]
				dependencies += current_depends
	
	# Remove already previously listed packages
	dependencies = [item for item in dependencies if item not in excluded_packages]

	if not dependencies:
		return dependencies
	else:
		return dependencies + get_dependencies(packages_list, dependencies, target_packages + excluded_packages)

# Gets the recommended packages for the target packages
def get_recommended(packages_list, target_packages):
	recommends = []
	current_recommends = []
	current_pkg = None

	for line in packages_list.splitlines():
		if line.startswith("Package:"):
			current_pkg = line.split(":", 1)[1].strip()
			current_recommends = []
		elif line.startswith("Recommends:"):
			if current_pkg in target_packages:
				current_recommends = line.split(":", 1)[1].strip().split(", ")
				# Remove alternatives
				current_recommends = [recommended.split(" | ")[0] for recommended in current_recommends]
				# Remove version specifier
				current_recommends = [recommended.split(" (")[0].strip() for recommended in current_recommends]
				recommends += current_recommends
	
	return recommends

def download_debs(filenames):
	for path in filenames:
		url = DEBIAN_URL + path
		file_name = os.path.basename(path)
		local_path = os.path.join(OUTPUT_DIR, file_name)
		
		if os.path.exists(local_path):
			print(f"Package already exists at location: {file_name}")
			continue
		
		print(f"Downloading: {file_name}...")
		try:
			response = requests.get(url)
			response.raise_for_status()
			with open(local_path, "wb") as f:
				f.write(response.content)
		except Exception as e:
			print(f"[Error] Failed to download '{file_name}': {e}")
	
	print(f"\n[Done] All files have been saved to: {os.path.abspath(OUTPUT_DIR)}")

# If there are to few arguments
if len(sys.argv) < 2:
	print("Usage: fetchdeb <package1> <package2> ...\nPlease specify at least one package to download.")
	sys.exit(1)

# Check internet connection and Packages.gz availability
try:
	print("Downloading Packages.gz...")
	response = requests.get(PACKAGES_GZ_URL, timeout=10)
	response.raise_for_status()
	packages_list = gzip.decompress(response.content).decode("utf-8")
except requests.exceptions.RequestException as e:
	print(f"[Error] Could not download Packages.gz: {e}\nPlease check your internet connection and try again.")
	sys.exit(1)
except Exception as e:
	print(f"[Error] Failed to process Packages.gz: {e}")
	sys.exit(1)

# Ask to get dependencies
if DOWNLOAD_DEPENDENCIES == False:
	try:
		if input("Download all required dependencies? [y/n]: ").strip().lower() in ("y", "yes"):
			DOWNLOAD_DEPENDENCIES = True
	except Exception as e:
		print(f"[Error] Failed to read input: {e}")
		# Default to not downloading dependencies

# Ask to get suggested packages
if DOWNLOAD_SUGGESTED == False:
	try:
		if input("Download recommended packages? [y/n]: ").strip().lower() in ("y", "yes"):
			DOWNLOAD_SUGGESTED = True
	except Exception as e:
		print(f"[Error] Failed to read input: {e}")
		# Default to not downloading recommended packages

# Get the arguments
try:
	target_packages = list(set(sys.argv[1:]))
	print(f"Fetching packages: {', '.join(target_packages)}")
except Exception as e:
	print(f"[Error] Failed to parse command line arguments: {e}")
	sys.exit(1)

filenames = get_filenames(packages_list, target_packages)

if not filenames:
	print("[Error] No matching packages found in the repository.")
	sys.exit(1)

if DOWNLOAD_DEPENDENCIES:
	try:
		dep_filenames = get_filenames(packages_list, get_dependencies(packages_list, target_packages, []))
		if dep_filenames:
			print(f"Found {len(dep_filenames)} dependencies to download.")
		filenames += dep_filenames
	except Exception as e:
		print(f"[Error] Failed to resolve dependencies: {e}")

if DOWNLOAD_SUGGESTED:
	try:
		rec_filenames = get_filenames(packages_list, get_recommended(packages_list, target_packages))
		if rec_filenames:
			print(f"Found {len(rec_filenames)} recommended packages to download.")
		filenames += rec_filenames
	except Exception as e:
		print(f"[Error] Failed to resolve recommended packages: {e}")

download_debs(filenames)
