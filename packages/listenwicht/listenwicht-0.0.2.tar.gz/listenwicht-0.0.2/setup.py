import setuptools

with open("README.md") as f:
	long_description = f.read()

setuptools.setup(
	name = "listenwicht",
	packages = setuptools.find_packages(),
	version = "0.0.2",
	license = "gpl-3.0",
	description = "Flexible Python-based mailing list daemon",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	author = "Johannes Bauer",
	author_email = "joe@johannes-bauer.com",
	url = "https://github.com/johndoe31415/listenwicht",
	download_url = "https://github.com/johndoe31415/listenwicht/archive/v0.0.2.tar.gz",
	keywords = [ "mailing", "list" ],
	install_requires = [ "mailcoil>=0.0.8" ],
	entry_points = {
		"console_scripts": [
			"listenwicht = listenwicht.__main__:main"
		]
	},
	include_package_data = True,
	classifiers = [
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3 :: Only",
		"Programming Language :: Python :: 3.12",
		"Programming Language :: Python :: 3.13",
	],
)
