import argparse
import yara
import apkid
import pkg_resources

def main():
	parser = argparse.ArgumentParser(description="APKiD - Android Application Identifier")
	parser.add_argument('files', metavar = 'FILE', type = str, nargs = "+", help = "apk, dex, or dir")
	parser.add_argument('-j', '--json' , action = 'store_true', help = "output results in JSON")
	parser.add_argument('-t', '--timeout', type = int, default = 30, help = 'Yara scan timeout in seconds')

	args = parser.parse_args()

	aid = apkid.APKiD(args.file, args.timeout, args.json)

	if not args.json:
		version = pkg_resources.get_distribution("apkid").version
		print "[!] APKiD %s :: from RedNaga :: rednaga.io" % version
	aid.scan()