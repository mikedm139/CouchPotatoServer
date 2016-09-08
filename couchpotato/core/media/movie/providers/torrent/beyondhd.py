from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.beyondhd import Base
from couchpotato.core.media.movie.providers.base import MovieProvider

log = CPLog(__name__)

autoload = 'BeyondHD'


class BeyondHD(MovieProvider, Base):
    
    cat_ids = [
        (['17', '49', '50', '77'], ['1080p']),
        (['61'], ['720p', '1080p']),
        (['75', '78'], ['720p']),
        (['94'], ['2160p']),
        (['37'], ['BR-disk']),
        (['71', '83'], ['1080p', '3d'])
    ]
