import traceback

from bs4 import BeautifulSoup
from couchpotato.core.helpers.encoding import toUnicode
from couchpotato.core.helpers.variable import tryInt, getIdentifier
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider


log = CPLog(__name__)


class Base(TorrentProvider):

    urls = {
        'test': 'https://beyond-hd.me/',
	'base': 'https://beyond-hd.me/%s',
        'search': 'https://beyond-hd.me/browse.php?searchin=title&incldead=0&search=%s',
 	'login': 'https://beyond-hd.me/pagelogin.php',
	'login_check': 'https://beyond-hd.me/messages.php',
	'detail': 'https://beyond-hd.me/details.php?id=%s',
	'nfo': 'https://beyond-hd.me/viewnfo.php?id=%s',
    }

    internals = ['61', '50', '83', '75', '49']

    remuxes = ['49', '17']

    login_fail_msg = 'Failed to login. Please confirm that your login link is correct and valid.'

    def _search(self, media, quality, results):

        url = self.urls['search'] % getIdentifier(media)

        data = self.getHTMLData(url)

        if data:
	    log.debug('Parsing data from BeyondHD')
            html = BeautifulSoup(data)

            try:
                result_table = html.find('table', attrs = {'class': 'tb_detail grey torrenttable', 'width': '900px', 'border': '1', 'cellspacing': '0', 'style': 'background-color:transparent;'})
                if result_table is None:
		    log.debug('BeyondHD provided no results.')
                    return

                entries = result_table.find_all('tr')
		log.debug('Parsing %d results from BeyondHD' % len(entries[1:]))
                for result in entries[1:]:

                    cells = result.find_all('td')
		    cat = cells[0].find('a')['href'].replace('browse.php?cat=', '')
		    log.debug('Category ID for result is: %s' % cat)
		    if cat in self.getCatId(quality):
			
			torrent_score = 0
			if self.conf('prefer_internal') and cat in self.internals:
			    log.debug('Found internal release. Boosting torrent score due to "Prefer Internal" setting.')
			    torrent_score += 1000
			if self.conf('prefer_remux') and cat in self.remuxes:
			    log.debug('Found Remux. Boosting torrent score due to "Prefer Remux" setting.')
			    torrent_score += 1000

                    	link = cells[2].find('a')['href']
			log.debug('Torrent link: %s' % link)
                    	
			torrent_id = link.replace('download.php?torrent=', '')
			log.debug('Torrent ID: %s' % torrent_id)

			title = cells[3].find('a').get_text()
			if cat != '37':
			    title = title.replace('BluRay ', '').replace('AVC ', '')
			log.debug('Release title: %s' % title)

			size = self.parseSize(cells[-4].get_text())
			log.debug('Release size: %d' % size)

			num_seeders = tryInt(cells[-2].string)
			log.debug('Number of Seeders for this release: %d' % num_seeders)

			num_leechers = tryInt(cells[-1].string)
			log.debug('Number of Leechers for this release: %d' % num_leechers)

			log.debug('This release gets a score of: %d' % torrent_score)

                    	results.append({
                            'id': torrent_id,
                            'name': title,
                            'url': self.urls['base'] % link,
                            'detail_url': self.urls['detail'] % torrent_id,
                            'size': size,
                            'seeders': num_seeders,
                            'leechers': num_leechers,
                            'get_more_info': self.getMoreInfo,
			    'score': torrent_score,
                    	})
		    else:
			pass

            except:
                log.error('Failed getting results from %s: %s', (self.getName(), traceback.format_exc()))

    def getMoreInfo(self, item):
        full_description = self.getHTMLData(self.urls['nfo'] % item['id'])
        html = BeautifulSoup(full_description)
        nfo_pre = html.find('td', attrs = {'class': 'text'})
        description = toUnicode(nfo_pre.text) if nfo_pre else ''

        item['description'] = description
        return item

    def getLoginParams(self):
        return {
            'qlogin': self.conf('login_link').replace('https://beyond-hd.me/pagelogin.php?qlogin=', '')
        }

    def loginSuccess(self, output):
        return 'index.php' in output.lower()

    loginCheckSuccess = loginSuccess


config = [{
    'name': 'beyondhd',
    'groups': [
        {
            'tab': 'searcher',
            'list': 'torrent_providers',
            'name': 'BeyondHD',
            'description': '<a href="https://beyond-hd.me" target="_blank">BeyondHD</a>',
            'wizard': True,
            'icon': 'https://beyond-hd.me/favicon.ico',
            'options': [
                {
                    'name': 'enabled',
                    'type': 'enabler',
                    'default': False,
                },
                {
                    'name': 'login_link',
		    'label': 'Login link',
		    'description': 'Generated in your BeyondHD profile',
                    'default': '',
                },
                {
                    'name': 'seed_ratio',
                    'label': 'Seed ratio',
                    'type': 'float',
                    'default': 1,
                    'description': 'Will not be (re)moved until this seed ratio is met.',
                },
                {
                    'name': 'seed_time',
                    'label': 'Seed time',
                    'type': 'int',
                    'default': 72,
                    'description': 'Will not be (re)moved until this seed time (in hours) is met.',
                },
                {
                    'name': 'prefer_internal',
                    'advanced': True,
                    'type': 'bool',
                    'label': 'Prefer Internal',
                    'default': 0,
                    'description': 'Favors Internal Releases over all other releases.'
                },
                {
                    'name': 'prefer_remux',
                    'advanced': True,
                    'type': 'bool',
                    'label': 'Prefer Remux',
                    'default': 0,
                    'description': 'Favors remuxes over all other releases.'
                },
                {
                    'name': 'extra_score',
                    'advanced': True,
                    'label': 'Extra Score',
                    'type': 'int',
                    'default': 20,
                    'description': 'Starting score for each release found via this provider.',
                },
            ],
        },
    ],
}]
