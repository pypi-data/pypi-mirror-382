import os
import logging
import kerbad

LOG = kerbad.getLogger()

import asyncio
import copy
from kerbad.common.factory import KerberosClientFactory, kerberos_url_help_epilog
from kerbad.common.target import KerberosTarget
from asysocks.unicomm.common.target import UniProto
from kerbad.common.spn import KerberosSPN
from kerbad.aioclient import AIOKerberosClient
from kerbad.common.kirbi import Kirbi
from kerbad.common.creds import KerberosCredential
from kerbad import logger

async def getTGS(kerberos_url, kirbifile = None):
	if isinstance(spn, str):
		spn = KerberosSPN.from_spn(spn)

	cu = KerberosClientFactory.from_url(kerberos_url)
	client = cu.get_client()
	LOG.debug('Getting TGT')
	await client.get_TGT()
	LOG.debug('Getting TGS for otherdomain krbtgt')
	ref_tgs, ref_encpart, ref_key, new_factory = await client.get_referral_ticket(spn.domain)
	kirbi = Kirbi.from_ticketdata(ref_tgs, ref_encpart)
	print(str(kirbi))
	if kirbifile is not None:
		kirbi.to_file(kirbifile)
	
	LOG.info('Done!')

def main():
	import argparse
	
	parser = argparse.ArgumentParser(description='Polls the kerberos service for a TGS for the sepcified user and specified service', formatter_class=argparse.RawDescriptionHelpFormatter, epilog = kerberos_url_help_epilog)
	parser.add_argument('-v', '--verbose', action='count', default=0)
	parser.add_argument('--kirbi', help='kirbi file to store the TGT ticket in, otherwise kirbi will be printed to stdout')
	parser.add_argument('kerberos_url', help='the kerberos target string. ')

	args = parser.parse_args()
	if args.verbose > 0:
		LOG.setLevel(logging.DEBUG)
	
	asyncio.run(getTGS(args.kerberos_url, args.kirbi))
	
if __name__ == '__main__':
	main()