import os
import datetime
#from sqlite.main import Connection, Cursor
from sqlite3 import Connection as LocalConnection
from sqlite3 import Row
#from useless.db.lowlevel import LocalConnection
from useless.db.midlevel import StatementCursor
from useless.db.lowlevel import tquery_lite


from useless.sqlgen.clause import Eq

from useless.base.path import path

from utbase import parse_wtprn_m3u_url
from utdbschema import generate_schema
from utguestxml import GuestElement
from utguestxml import GuestElementParser

DOUBLE_BS = '\\'
SINGLE_BS = DOUBLE_BS[0]
ESCAPED_ENDL = DOUBLE_BS + 'n'
def unescape_text(text):
    return text.replace(ESCAPED_ENDL, '\n')

def datefromstring(dstring):
    return datetime.date(*map(int, dstring.split('-')))

def attribute_factory(cursor, row):
    rs = ResultSet(row)
    rs.setup_cursor(cursor)
    return rs

class ResultSetRow(Row):
    def __init__(self, cursor, row):
        Row.__init__(self, cursor, row)
        self._cursor = cursor

    def __getattr__(self, attr):
        return Row.__getitem__(self, attr)

    def __repr__(self):
        rowtuple = tuple(self[index] for index in range(len(self)))
        return '%s%s' % (self.__class__.__name__, str(rowtuple))
    

class ResultSet(tuple):
    def __init__(self, row):
        tuple.__init__(self, row)
        self._orig_row = row
        
    def setup_cursor(self, cursor):
        self._cursor = cursor
        self._dict = dict()
        for idx, col in enumerate(cursor.description):
            attr = col[0]
            value = self[idx]
            #print 'attr, value', attr, value
            setattr(self, attr, value)
            self._dict[attr] = value

    def __getitem__(self, key):
        if type(key) is int:
            return tuple.__getitem__(self, key)
        else:
            return self._dict[key]
    

class tt(tuple):
    def __init__(self, row, ignore=True):
        tuple.__init__(self, row)
        
class Connection(LocalConnection):
    def __init__(self, dbname='test.db', autocommit=1, encoding='utf-8'):
        isolation_level = ''
        if autocommit:
            isolation_level = None
        LocalConnection.__init__(self, dbname, isolation_level=isolation_level)
        #self.row_factory = ResultSet
        #self.row_factory = attribute_factory
        #self.row_factory = Row
        self.row_factory = ResultSetRow
        
    def stmtcursor(self):
        cursor = StatementCursor(self)
        cursor.__dbtype__ = 'lite'
        cursor.__tquery__ = tquery_lite
        return cursor


class Guests(object):
    def __init__(self, conn):
        self.conn = conn
        cursor = self.conn.stmtcursor()
        if not cursor.tables():
            generate_schema(cursor)
            if os.environ.has_key('UTDB_TESTING'):
                data = dict(firstname='joe', lastname='sixpack')
                cursor.insert('guests', data)
                data['lastname'] = 'schmoe'
                cursor.insert('guests', data)
                data['firstname'] = 'john'
                data['lastname'] = 'doe'
                cursor.insert('guests', data)
            

    def get_guest_data(self, guestid):
        clause = Eq('guestid', guestid)
        cursor = self.conn.stmtcursor()
        rows = cursor.select(table='guests', clause=clause)
        return rows[0]

    def update_guest_data(self, data):
        guestid = data['guestid']
        clause = Eq('guestid', guestid)
        cursor = self.conn.stmtcursor()
        cursor.update(table='guests', data=data, clause=clause)

    def insert_guest_data(self, data):
        cursor = self.conn.stmtcursor()
        cursor.insert(table='guests', data=data)

    def get_guest_rows(self):
        cursor = self.conn.stmtcursor()
        return cursor.select(table='guests', order='guestid')

    ######################
    # works methods      #
    ######################
    def get_guest_works(self, guestid):
        cursor = self.conn.stmtcursor()
        table = 'all_works natural join guest_works'
        clause = Eq('guestid', guestid)
        return cursor.select(table=table, clause=clause, order=['type'])

    def get_single_work(self, workid):
        cursor = self.conn.stmtcursor()
        clause = Eq('workid', workid)
        table = 'all_works'
        rows = cursor.select(table=table, clause=clause)
        return rows[0]

    def update_work(self, workid, data):
        clause = Eq('workid', workid)
        table = 'all_works'
        cursor = self.conn.stmtcursor()
        cursor.update(table=table, data=data, clause=clause)
        
        
    def insert_new_work(self, guestid, data):
        cursor = self.conn.stmtcursor()
        cursor.insert('all_works', data)
        workid = int(cursor.max('workid', 'all_works')[0]['max(workid)'])
        reldata = dict(guestid=guestid, workid=workid)
        cursor.insert('guest_works', reldata)


    ###########################
    # appearances methods     #
    ###########################
    def get_appearances(self, guestid):
        cursor = self.conn.stmtcursor()
        table = 'appearances'
        clause = Eq('guestid', guestid)
        return cursor.select(table=table, clause=clause, order=['url'])

    # the url here is the .m3u url from wtrpn archives page
    def insert_new_appearance(self, guestid, url):
        cursor = self.conn.stmtcursor()
        showdate = parse_wtprn_m3u_url(url)
        data = dict(guestid=guestid, showdate=showdate, url=url)
        cursor.insert('appearances', data)
        

    ###########################
    # pictures methods        #
    ###########################
    def insert_new_picture(self, guestid, data):
        cursor = self.conn.stmtcursor()
        cursor.insert('all_pictures', data)
        pixnum = int(cursor.max('pixnum', 'all_pictures')[0]['max(pixnum)'])
        reldata = dict(guestid=guestid, pixnum=pixnum)
        cursor.insert('guest_pictures', reldata)

    def get_guest_pictures(self, guestid):
        cursor = self.conn.stmtcursor()
        table = 'all_pictures natural join guest_pictures'
        clause = Eq('guestid', guestid)
        order = ['all_pictures.pixnum']
        return cursor.select(table=table, clause=clause, order=order)

    def get_guest_picture_filenames(self, guestid):
        return [row['all_pictures.filename'] for row in self.get_guest_pictures(guestid)]
    
    def export_guest_xml(self, guestid, picturepath):
        picturepath = path(picturepath)
        data = self.get_guest_data(guestid)
        element = GuestElement()
        for att in ['firstname', 'lastname', 'salutation']:
            value = data[att]
            if value is None:
                value = ''
            element.setAttribute(att, value)
        if data['title'] is not None:
            element.title_element.set(data['title'])
        if data['description'] is not None:
            element.desc_element.set(data['description'])
        for row in self.get_appearances(guestid):
            element.appearances.add_appearance(row['showdate'].date)
        for row in self.get_guest_works(guestid):
            url = row['all_works.url']
            wtype = row['all_works.type']
            title = row['all_works.title']
            description = row['all_works.description']
            element.works.add_work(url=url, type=wtype, title=title, description=description)
        for filename in self.get_guest_picture_filenames(guestid):
            element.pictures.add_picture(picturepath / filename)
        return element
    

    def _get_guestid(self, firstname, lastname):
        cursor = self.conn.stmtcursor()
        clause = Eq('firstname', firstname) & Eq('lastname', lastname)
        table = 'guests'
        rows = cursor.select(table=table, clause=clause)
        if not rows or len(rows) > 1:
            raise RuntimeError, 'Guest not imported'
        return rows[0]['guestid']
        
    def _wtprn_url_dates(self, date):
        year = str(date.year)
        year2 = '%02d' % (date.year % 100)
        month2 = '%02d' % date.month
        day2 = '%02d' % date.day
        wday = date.strftime('%a')
        return year, year2, month2, day2, wday
    
    def _base_wtprn_url(self, date):
        year, year2, month2, day2, wday = self._wtprn_url_dates(date)
        url = 'http://mp3.wtprn.com/Albrecht/%s%s/' % ( year2, month2)
        return url

    
    def _wtprn_file(self, date, ext):
        year, year2, month2, day2, wday = self._wtprn_url_dates(date)
        base = self._base_wtprn_url(date)
        filename = '%s%s%s_%s_Albrecht.%s' % (year, month2, day2, wday, ext)
        return base + filename

    def import_guest_xml(self, filename, picturepath):
        parser = GuestElementParser()
        parser.parse_file(filename)
        self.insert_guest_data(parser.main_row)
        firstname = parser.main_row['firstname']
        lastname = parser.main_row['lastname']
        guestid = self._get_guestid(firstname, lastname)
        for appearance in parser.appearances:
            appearance = datefromstring(appearance)
            m3u = self._wtprn_file(appearance, 'm3u')
            self.insert_new_appearance(guestid, m3u)
        for work in parser.works:
            self.insert_new_work(guestid, work)
        for picture in parser.pictures:
            self.insert_new_picture(guestid, dict(filename=picture['filename']))
            filename = picturepath / picture['filename']
            pfile = filename.open('w')
            pfile.write(picture['data'])
            pfile.close()
            
        
    
if __name__ == '__main__':
    import os
    dbfile = 'test.db'
    if os.environ.has_key('UTDBFILE'):
        dbfile = os.environ['UTDBFILE']
    conn = Connection(dbname=dbfile,
                      autocommit=True, encoding='ascii')
    cursor = conn.stmtcursor()
    cursor.set_table('guests')
    picturepath = path(dbfile).dirname()
    g = Guests(conn)
    x = g.export_guest_xml(12, picturepath)
    from StringIO import StringIO
    xf = StringIO()
    data = x.toxml('utf-8')
    xf.write(data)
    xf.seek(0)
    gep = GuestElementParser()
    gep.parse_file(xf)
    
    
    # using this to make the html page for kma
    from utdoc import AllGuestsDoc
    # we need a fake app class to get the
    # doc object to work correctly
    class FakeApp(object):
        def __init__(self, conn):
            self.guests = Guests(conn)
            self.datadir = os.path.dirname(dbfile)

    def makedoc():
        app = FakeApp(conn)
        guests = app.guests.get_guest_rows()
        doc = AllGuestsDoc(app)
        doc.set_info_manually(guests)
        f = file('utguests.html', 'w')
        f.write(doc.output())
        f.close()
        print 'html output complete'
        
    def parse_url(url):
        import urlparse
        import datetime
        utuple = urlparse.urlparse(url)
        m3u_filename = utuple[2].split('/')[-1]
        show_date = m3u_filename.split('_')[0]
        year = int(show_date[:4])
        month = int(show_date[4:6])
        day = int(show_date[6:8])
        date = datetime.date(year, month, day)
        return date
    
    def fill_datecol():
        from useless.sqlgen.clause import Eq
        cursor.set_table('appearances')
        rows = cursor.select()
        for row in rows:
            date = parse_url(row['url'])
            clause = Eq('guestid', row['guestid']) & Eq('url', row['url'])
            #print date, clause
            cursor.update(data=dict(showdate=date), clause=clause)
            #print row
