__version__ = '2.5'
__author__  = 'Tivise'

import b3
import re
import b3.events
import b3.plugin
import b3.cron
import datetime, time, calendar, threading, thread
from time import gmtime, strftime

def cdate():
	time_epoch = time.time() 
	time_struct = time.gmtime(time_epoch)
	date = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
	mysql_time_struct = time.strptime(date, '%Y-%m-%d %H:%M:%S')
	cdate = calendar.timegm( mysql_time_struct)
	return cdate

class TivmodPlugin(b3.plugin.Plugin):
    _cronTab = None 
    _maxTopOutput = 5
    requiresConfigFile = True
    statsTable = 'dinero'
    def onLoadConfig(self):
        try:
              self._minlevel_level = self.config.getint('settings', 'minlevel_level')
        except:
            self._minlevel_level = 0 
        try:
              self._minlevel_money = self.config.getint('settings', 'minlevel_money')
        except:
            self._minlevel_money = 0 
        try:
              self._minlevel_kill = self.config.getint('settings', 'minlevel_kill')
        except:
            self._minlevel_kill = 0 
        try:
              self._minlevel_teleport = self.config.getint('settings', 'minlevel_teleport')
        except:
            self._minlevel_teleport = 0 
        try:
              self._minlevel_givemoney = self.config.getint('settings', 'minlevel_givemoney')
        except:
            self._minlevel_givemoney = 100 
        try:
              self._minlevel_givexp = self.config.getint('settings', 'minlevel_givexp')
        except:
            self._minlevel_givexp = 100
        try:
              self._minlevel_god = self.config.getint('settings', 'minlevel_god')
        except:
            self._minlevel_god = 0 
        try:
              self._price_kill = self.config.getint('settings', 'price_kill')
        except:
            self._price_kill = 7500 
        try:
              self._price_teleport = self.config.getint('settings', 'price_teleport')
        except:
            self._price_teleport = 3000 
        try:
              self._price_god = self.config.getint('settings', 'price_god')
        except:
            self._price_god = 7500 
        try:
              self._hit_win_money = self.config.getint('settings', 'hit_win_money')
        except:
            self._hit_win_money = 20
        try:
              self._hit_win_xp = self.config.getint('settings', 'hit_win_xp')
        except:
            self._hit_win_xp = 40
        try:
              self._message_help = self.config.getint('settings', 'message_help')
        except:
            self._message_help = '^7You earned money and you can win a level up when you hit a red player, to see your level/money use !level ^2<^5player^2>^7 or !money ^2<^5player^2>'
    def onStartup(self):
        # get the admin plugin so we can register commands
        self.registerEvent(b3.events.EVT_CLIENT_TEAM_CHANGE)
        self.registerEvent(b3.events.EVT_CLIENT_DISCONNECT)
        self.registerEvent(b3.events.EVT_GAME_ROUND_START)
        self.registerEvent(b3.events.EVT_CLIENT_DAMAGE)
        self.registerEvent(b3.events.EVT_CLIENT_JOIN)
        self.registerEvent(b3.events.EVT_CLIENT_AUTH)
        self.registerEvent(b3.events.EVT_CLIENT_KILL)
        self.registerEvent(b3.events.EVT_GAME_EXIT)
        self._adminPlugin = self.console.getPlugin('admin')
        self.query = self.console.storage.query
        
        if not self._adminPlugin: 
            
            self.error(':p -Tivise- demain il neige ! :p')
            return
        else:	

         # Register commands
         self._adminPlugin.registerCommand(self, 'level', self._minlevel_level, self.cmd_level, 'lvl')
         self._adminPlugin.registerCommand(self, 'nombrekill', 100, self.cmd_nombrekill, 'nkill')
         self._adminPlugin.registerCommand(self, 'bonnuskill', 100, self.cmd_bonnuskill, 'bkill')
         self._adminPlugin.registerCommand(self, 'multipliers', 100, self.cmd_multiplier, 'multi')
         self._adminPlugin.registerCommand(self, 'money', self._minlevel_money, self.cmd_money, 'mo')
         self._adminPlugin.registerCommand(self, 'kill', self._minlevel_kill, self.cmd_kill, 'kl')
         self._adminPlugin.registerCommand(self, 'teleport', self._minlevel_teleport, self.cmd_teleport, 'tp')
         self._adminPlugin.registerCommand(self, 'givemoney', self._minlevel_givemoney, self.cmd_givemoney, 'gm')
         self._adminPlugin.registerCommand(self, 'givexp', self._minlevel_givexp, self.cmd_givexp, 'ge')
         self._adminPlugin.registerCommand(self, 'pay', 0, self.cmd_pay, 'payplayer')
         self._adminPlugin.registerCommand(self, 'god', self._minlevel_god, self.cmd_god, 'gd')
         self._adminPlugin.registerCommand(self, 'xlrtopprestige', 0, self.cmd_xlrtopprestige, 'topprestige')
         self._adminPlugin.registerCommand(self, 'buylist', 0, self.cmd_buy, 'bl')
         self._adminPlugin.registerCommand(self, 'moneyhelp', 0, self.cmd_moneyhelp, 'mh')
         self._adminPlugin.registerCommand(self, 'topmoney', 0, self.cmd_topmoney, 'topmo')
        if 'commands' in self.config.sections():
		   for cmd in self.config.options('commands'):
			level = self.config.get('commands', cmd)
			sp = cmd.split('-')
			alias = None
			if len(sp) == 2:
				cmd, alias = sp
			func = self.getCmd(cmd)
			if func:
				self._adminPlugin.registerCommand(self, cmd, level, func, alias)
		
    def getCmd(self, cmd):
        cmd = 'cmd_%s' % cmd
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            return func

        return None
		
    def onEvent(self, event):
##EVENT CLIENT TEAM CHANGE:
        if(event.type == b3.events.EVT_CLIENT_TEAM_CHANGE):
           self.Namechange(event.client, event.target, event.data)
           self.Funstuff(event.client, event.target, event.data)

##EVENT CLIENT JOIN:
        if(event.type == b3.events.EVT_CLIENT_JOIN):
           self.Namechange(event.client, event.target, event.data)
           self.Funstuff(event.client, event.target, event.data)

## CLIENT KILL:
        if(event.type == b3.events.EVT_CLIENT_DAMAGE): 
           self.knifeKill(event.client, event.target, event.data)


## CLIENT KILL:
        if(event.type == b3.events.EVT_CLIENT_KILL): 
           self.knifeKill(event.client, event.target, event.data)
		  
		   ## CLIENT AUTH:
        if(event.type == b3.events.EVT_CLIENT_AUTH):
          sclient = event.client
          q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (sclient.id))
          self.debug(q)
          cursor = self.console.storage.query(q)
          if(cursor.rowcount == 0):
              q=('INSERT INTO `dinero`(`azul`, `precio_azul`, `rojo`, `precio_rojo`, `idioma`, `dinero`, `level`, `firstname`, `iduser`, `expPoints`, `prestige`, `totalexpPoints`, `multiplier`, `statsbonnuskills`) VALUES (0,0,0,0,0,2500,1,0,%s,0,0,300,0,0)' % (sclient.id))
              self.console.storage.query(q)
          cursor.close()
          q=('UPDATE `dinero` SET `firstname` = "%s" WHERE iduser = "%s"' % (sclient.exactName, sclient.id))
          self.console.storage.query(q)
          cursor.close()
          self.deconnection(event.client, event.target, event.data)
          self.Namelevelkill(event.client, event.target, event.data)
		  
## CLIENT DISCONNECT:	  
        if(event.type == b3.events.EVT_CLIENT_DISCONNECT):
          sclient = event.client
          q=('DELETE FROM automoney WHERE client_id = "%s"' % (sclient.id))
          self.console.storage.query(q)
          self.deconnection(event.client, event.target, event.data)
## GAME EXIT:
        if(event.type == b3.events.EVT_GAME_EXIT):
           q=('SELECT * FROM `dinero` WHERE `dinero` > "0"')
           cursor = self.console.storage.query(q)
           r = cursor.getRow()
           dinero = r['dinero']
    	   q=('UPDATE `dinero` SET `dinero` = dinero+300 WHERE `enligne` > "0"')
           self.console.storage.query(q)
           self.console.say('^5You stay connected one more map, you get ^1[^2300^1] ^5coins !')
## GAME ROUND START:
        if(event.type == b3.events.EVT_GAME_ROUND_START):
           q=('SELECT * FROM `dinero` WHERE `dinero` > "0"')
           cursor = self.console.storage.query(q)
           r = cursor.getRow()
           dinero = r['dinero']
    	   q=('UPDATE `dinero` SET `dinero` = dinero+100 WHERE `enligne` > "0"')
           self.console.storage.query(q)
           self.console.say('^5You stay connected one round, you get ^1[^2100^1] ^5coins !')
## CLIENT TEAM CHANGE:
		  
    def TeamBlue(self):
    	blue = []
    	for c in self.console.clients.getList():
    	  if(c.team == b3.TEAM_BLUE):
    	    blue.append(c.cid)
    	return blue
    	# something is wrong, can't start without admin plugin
			
    def TeamRed(self):
    	red = []
    	for c in self.console.clients.getList():
    	  if(c.team == b3.TEAM_RED):
    	    red.append(c.cid)
    	return red
		
    def get_client_location(self, client):
        if client.isvar(self,'localization'):
            return client.var(self, 'localization').value    
        else:
            try:
                ret = geoip.geo_ip_lookup(client.ip)
                if ret:
                    client.setvar(self, 'localization', ret)
                return ret
            except Exception, e:
                self.error(e)
                return False
    def knifeKill(self, client, target, data=None):
    	  if client:
    	    q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
    	    cursor = self.console.storage.query(q)
    	    r = cursor.getRow()
    	    iduser = r['iduser']
            expPoints = r['expPoints']
            statsbonnuskills = r['statsbonnuskills']
            level = r['level']
            dinero = r['dinero']
            multiplier = r['multiplier']
            prestige = r['prestige']
            totalexpPoints = r['totalexpPoints']
## FOR KILL !
    	    if(client.team == b3.TEAM_RED) or (client.team == b3.TEAM_BLUE):
              q=('UPDATE `dinero` SET `expPoints` = expPoints+%s WHERE iduser = "%s"' % (self._hit_win_xp, client.id))
              self.console.storage.query(q)
              if(totalexpPoints <= (expPoints+600)):
                q=('UPDATE `dinero` SET `level` = level+1 WHERE iduser = "%s"' % (client.id))
                self.console.storage.query(q)
              if(multiplier > 0):
                  q=('UPDATE `dinero` SET `expPoints` = expPoints+multiplier WHERE iduser = "%s"' % (client.id))
                  self.console.storage.query(q)      				
              if(totalexpPoints <= (expPoints+600)):
                  q=('UPDATE `dinero` SET `statsbonnuskills` = statsbonnuskills+1 WHERE iduser = "%s"' % (client.id))
                  self.console.storage.query(q)
              if(totalexpPoints <= (expPoints+600)):
                 q=('UPDATE `dinero` SET `totalexpPoints` = totalexpPoints+900 WHERE iduser = "%s"' % (client.id))
                 self.console.storage.query(q)
              if(totalexpPoints <= (expPoints+600)):
                 q=('UPDATE `dinero` SET `expPoints` = expPoints-expPoints WHERE iduser = "%s"' % (client.id))
                 self.console.storage.query(q)
                 client.message('^7Level ^5UP^7: ^2%s' % (level+1))
                 self.console.write('spoof %s say ^7I reach level ^2[^5%s^2]' % (client.cid, level+1))
## LEVEL 50
              if(level == 50):
                  q=('UPDATE `dinero` SET `dinero` = dinero+8000 WHERE iduser = "%s"' % (client.id))
                  self.console.storage.query(q)
              if(level == 50):
                  q=('UPDATE `dinero` SET `level` = level+1 WHERE iduser = "%s"' % (client.id))
                  self.console.storage.query(q)
                  client.message('^7Level ^5UP^7: ^251 ^5[^2+8000 coins^5]')
## LEVEL 20
              if(level == 20):
                  q=('UPDATE `dinero` SET `dinero` = dinero+5000 WHERE iduser = "%s"' % (client.id))
                  self.console.storage.query(q)
              if(level == 20):
                  q=('UPDATE `dinero` SET `level` = level+1 WHERE iduser = "%s"' % (client.id))
                  self.console.storage.query(q)
                  client.message('^7Level ^5UP^7: ^221 ^5[^2+5000 coins^5]')
## LEVEL 40
              if(level == 40):
                  q=('UPDATE `dinero` SET `dinero` = dinero+7500 WHERE iduser = "%s"' % (client.id))
                  self.console.storage.query(q)
              if(level == 40):
                  q=('UPDATE `dinero` SET `level` = level+1 WHERE iduser = "%s"' % (client.id))
                  self.console.storage.query(q)
                  client.message('^7Level ^5UP^7: ^241 ^5[^2+7500 coins^5]')
## LEVEL 60
              if(level == 60):
                  q=('UPDATE `dinero` SET `dinero` = dinero+10000 WHERE iduser = "%s"' % (client.id))
                  self.console.storage.query(q)
              if(level == 60):
                  q=('UPDATE `dinero` SET `level` = level+1 WHERE iduser = "%s"' % (client.id))
                  self.console.storage.query(q)
                  client.message('^7Level ^5UP^7: ^261 ^5[^2+10000 coins^5]')
## LEVEL 70
              if(level == 70):
                  q=('UPDATE `dinero` SET `dinero` = dinero+15000 WHERE iduser = "%s"' % (client.id))
                  self.console.storage.query(q)
              if(level == 70):
                  q=('UPDATE `dinero` SET `level` = level+1 WHERE iduser = "%s"' % (client.id))
                  self.console.storage.query(q)
                  client.message('^7Level ^5UP^7: ^271 ^5[^2+15000 coins^5]')
## LEVEL 80
              if(level == 80):
                  q=('UPDATE `dinero` SET `dinero` = dinero+20000 WHERE iduser = "%s"' % (client.id))
                  self.console.storage.query(q)
              if(level == 80):
                  q=('UPDATE `dinero` SET `level` = level+1 WHERE iduser = "%s"' % (client.id))
                  self.console.storage.query(q)
                  client.message('^7Level ^5UP^7: ^281 ^5[^2+20000 coins^5]')
## LEVEL 90
              if(level == 90):
                  q=('UPDATE `dinero` SET `dinero` = dinero+30000 WHERE iduser = "%s"' % (client.id))
                  self.console.storage.query(q)
              if(level == 90):
                  q=('UPDATE `dinero` SET `level` = level+1 WHERE iduser = "%s"' % (client.id))
                  self.console.storage.query(q)
                  client.message('^7Level ^5UP^7: ^291 ^5[^2+30000 coins^5]')
              if(level == 100):
                  q=('UPDATE `dinero` SET `dinero` = dinero+50000 WHERE iduser = "%s"' % (client.id))
                  self.console.storage.query(q)
## LEVEL 100
              if(level == 100):
                 q=('UPDATE `dinero` SET `totalexpPoints` = 300 WHERE iduser = "%s"' % (client.id))
                 self.console.storage.query(q)
              if(level == 100):
                 q=('UPDATE `dinero` SET `expPoints` = expPoints-expPoints WHERE iduser = "%s"' % (client.id))
                 self.console.storage.query(q)
              if(level == 100):
                 q=('UPDATE `dinero` SET `prestige` = prestige+1 WHERE iduser = "%s"' % (client.id))
                 self.console.storage.query(q)
              if(level == 100):
                 q=('UPDATE `dinero` SET `level` = level-level WHERE iduser = "%s"' % (client.id))
                 self.console.storage.query(q)
                 self.console.write('bigtext "%s: ^7Prestige ^5UP^7: ^6%s"' % (client.exactName, prestige+1))
    	    q=('UPDATE `dinero` SET `dinero` = dinero+%s WHERE iduser = "%s"' % (self._hit_win_money, client.id))
    	    self.console.storage.query(q)
          cursor.close() 
    def Funstuff(self, client, target, data=None):
## FOR FUNSTUFF
        q=('SELECT * from `dinero` WHERE `iduser` = "%s"' % (client.id))
    	cursor = self.console.storage.query(q)
    	r = cursor.getRow()
        iduser = r['iduser']
        level = r['level']
        if(client.team == b3.TEAM_RED):
          if (level > 9):
            self.console.write('forcecvar %s funred patch,phat,ninja' % (client.cid))
          else:
            self.console.write('forcecvar %s funred touqrd' % (client.cid))
    	if(client.team == b3.TEAM_BLUE):
          if (level > 9):
            self.console.write('forcecvar %s funblue patch,viking,ninja' % (client.cid))
          else:
            self.console.write('forcecvar %s funblue touqwt ' % (client.cid))

    def Namelevelkill(self, client, target, data=None):
          q=('SELECT * from `clients` WHERE `id` = "%s"' % (client.id))
    	  cursor = self.console.storage.query(q)
    	  r = cursor.getRow()
          id = r['id']
    	  r = cursor.getRow()
          connections = r['connections']
          firstname = r['firstname']
          if id == client.id:
    	    if (connections < 2):
              q=('UPDATE `clients` SET `firstname` = "%s" WHERE id = "%s"' % (client.exactName, client.id))
              self.console.storage.query(q)
            cursor.close()

    def Namechange(self, client, target, data=None):
    	  if client:
            q=('SELECT * from `clients` WHERE `id` = "%s"' % (client.id))
    	    cursor = self.console.storage.query(q)
    	    r = cursor.getRow()
            firstname = r['firstname']			
    	    q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
    	    cursor = self.console.storage.query(q)
    	    r = cursor.getRow()			
            level = r['level']
            iduser = r['iduser']
            self.console.write('forcecvar %s name ^2[^7%s^2]^7%s' % (client.cid, level, firstname))

    def cmd_level(self, data, client, cmd=None):
        if data is None or data=='':
          if(client.maxLevel > 110):
            client.message('^7DEMAIN IL NEIGE <3')
            return True
          else:  
            q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
            cursor = self.console.storage.query(q)
            r = cursor.getRow()
            iduser = r['iduser']
            level = r['level']
            dinero = r['dinero']
            expPoints = r['expPoints']
            prestige = r['prestige']
            totalexpPoints = r['totalexpPoints']
            client.message('^7Prestige: ^6%s ^7Level: ^2%s ^7expPoints: ^1%s ^8// ^1%s ^2Coins: [^5%s^2]' % (prestige, level, expPoints, totalexpPoints, dinero))
            cursor.close()
            return True
        else:
          input = self._adminPlugin.parseUserCmd(data)
          sclient = self._adminPlugin.findClientPrompt(input[0], client)
          if not sclient: return False
          if(sclient.maxLevel > 100):
            client.message('%s ^7is Super Admin ^5[^2100^5] ^7so he/she dont have level!' % (sclient.exactName))
            return True
          else:
            q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (sclient.id))
            cursor = self.console.storage.query(q)
            r = cursor.getRow()
            iduser = r['iduser']
            dinero = r['dinero']
            level= r['level']
            prestige = r['prestige']
            expPoints = r['expPoints']
            totalexpPoints = r['totalexpPoints']
            client.message('%s:^7 Prestige: ^6%s^7 Level: ^2%s ^7expPoints: ^1%s ^8// ^1%s ^2Coins: [^5%s^2]' % (sclient.exactName, prestige, level, expPoints, totalexpPoints, dinero))
            cursor.close()
            return True
			
    def cmd_nombrekill(self, data, client, cmd=None):
        if data is None or data=='':
          if(client.maxLevel == 80):
            client.message('^7Demain il neige')
            return True
          else:
            q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
            cursor = self.console.storage.query(q)
            r = cursor.getRow()
            iduser = r['iduser']
            statsbonnuskills = r['statsbonnuskills']
            client.message('^7You can kill players: ^2%s ^7times' % (statsbonnuskills))
            cursor.close()
            return True
        else:
          input = self._adminPlugin.parseUserCmd(data)
          sclient = self._adminPlugin.findClientPrompt(input[0], client)
          if not sclient: return False
          if(sclient.maxLevel == 80):
            client.message('%s contient ^2Infinits' % (sclient.exactName))
            return True
          else:
            q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (sclient.id))
            cursor = self.console.storage.query(q)
            r = cursor.getRow()
            iduser = r['iduser']
            statsbonnuskills = r['statsbonnuskills']
            client.message('%s:^7He can kill players: ^2%s ^7times' % (sclient.exactName, statsbonnuskills))
            cursor.close()
            return True
			
			
    def cmd_bonnuskill(self, data, client, cmd=None):
        if data:
            sclient = self._adminPlugin.findClientPrompt(data, client)
        else:
            client.message('Use !bkill <player>')
            return
        if(sclient.maxLevel == 80):
            client.message('%s demain il neige' % (sclient.exactName))
            return True
        if sclient:
            q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (sclient.id))
            cursor = self.console.storage.query(q)
            r = cursor.getRow()
            iduser = r['iduser']
            statsbonnuskills = r['statsbonnuskills']
            if(statsbonnuskills+1 > 1):
               self.console.write('smite %s' % (sclient.cid))
               q=('UPDATE `dinero` SET `statsbonnuskills` = statsbonnuskills-1 WHERE iduser = "%s"' % (client.id))
               self.console.storage.query(q)
                   
            else:
			   client.message('^1You do not have to kill Bonus')
			   
			       
            cursor.close()
            return True
			
    def cmd_multiplier(self, data, client, cmd=None):
        if data:
            input = self._adminPlugin.parseUserCmd(data)
        else:
            client.message('^7Use !bonnuslevel ^2<^5number^2>')
            return
        radio = input[0]
        if int(radio):
          q=('SELECT * FROM `dinero`')
          cursor = self.console.storage.query(q)
          r = cursor.getRow()
          iduser = r['iduser']
          multiplier = r['multiplier']
          q=('UPDATE `dinero` SET `multiplier` = "%s"' % (radio))
          self.console.storage.query(q)
          self.console.write('bigtext "^1Bonus^7: +^5%s"' % (radio))
          cursor.close()		  
			   
    def cmd_xlrtopprestige(self, data, client, cmd=None, ext=False):
	 """\
	 - Displays the players with best prestige(s)
	 """
	 prestige = 'prestige'
	 thread.start_new_thread(self.getTopStats, (client, cmd, ext, prestige))
	 return

    def getTopStats(self, client, cmd, ext, prestige):
      q = 'SELECT * FROM %s WHERE (`prestige` > 0) ORDER BY `prestige` DESC LIMIT %s' % (self.statsTable, self._maxTopOutput)
      self.debug(q)
      cursor = self.query(q)
      if cursor and (cursor.rowcount > 0):
        message = ('^3Top %s most %se :' % (self._maxTopOutput, prestige[:-1]))
        if ext:
            self.console.say(message)
        else:
           cmd.sayLoudOrPM(client, message)
        c = 1
        while not cursor.EOF:
            r = cursor.getRow()
            message = '^2[^3#%s^2]^7:^3@%s^7>%s^7-^5[^2%s ^6prestige^5]' % (
                c, r['iduser'], r['firstname'], r[prestige])
            if ext:
                self.console.say(message)
            else:
                cmd.sayLoudOrPM(client, message)
            cursor.moveNext()
            c += 1
            time.sleep(1)
      else:
		message = 'No prestige %sd yet!' % prestige[:-1]
		if ext:
			self.console.say(message)
		else:
			cmd.sayLoudOrPM(client, message)
		return None
      return	
    def cmd_money(self, data, client, cmd=None):
        if data is None or data=='':
          if(client.maxLevel > 100):
            client.message('^7Contient Infinit')
            return True
          else:  
            q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
            cursor = self.console.storage.query(q)
            r = cursor.getRow()
            iduser = r['iduser']
            dinero = r['dinero']
            idioma = r['idioma']
            client.message('^7You have:^2[^5%s^2] ^7Coins' % (dinero))
            cursor.close()
            return True
        else:
          input = self._adminPlugin.parseUserCmd(data)
          sclient = self._adminPlugin.findClientPrompt(input[0], client)
          if not sclient: return False
          if(sclient.maxLevel > 100):
            client.message('%s Contient ^2Infinit' % (sclient.exactName))
            return True
          else:
            q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (sclient.id))
            cursor = self.console.storage.query(q)
            r = cursor.getRow()
            iduser = r['iduser']
            dinero = r['dinero']
            idioma = r['idioma']
            client.message('%s ^7has:^2[^5%s^2] ^7Coins' % (sclient.exactName,dinero))
            cursor.close()
            return True

    def cmd_kill(self, data, client, cmd=None):
      if(client.maxLevel > 100):
        input = self._adminPlugin.parseUserCmd(data)
        sclient = self._adminPlugin.findClientPrompt(input[0], client)
        self.console.write("kill %s" % (sclient.cid))
      else:
    	  q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
    	  cursor = self.console.storage.query(q)
    	  r = cursor.getRow()
    	  iduser = r['iduser']
    	  dinero = r['dinero']
    	  idioma = r['idioma']
    	  input = self._adminPlugin.parseUserCmd(data)
    	  if not data:
    	  	client.message('^7Type !kill ^5<^2player^5>')
    	  	return False
    	  sclient = self._adminPlugin.findClientPrompt(input[0], client)
    	  if not sclient: return False
    	  if (dinero > self._price_kill):
    	    if((client.team == b3.TEAM_BLUE) != (sclient.team == b3.TEAM_BLUE)) or ((client.team == b3.TEAM_RED) != (sclient.team == b3.TEAM_RED)):
    	      q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (self._price_kill, client.id))
    	      self.console.storage.query(q)
    	      self.console.write("kill %s" % (sclient.cid))
    	      client.message('^7you killed a %s' % (sclient.exactName))
    	      return True
    	    else:
    	    	client.message('^7You can only Kill ^5[^6Enemies^5]')
    	    	return False
    	  else:
    	  	client.message('^6You dont have coins. ^7Your money is: ^5[^6%s^5] ^7and you need ^5[^2%s^5]^7 more for Kill' % dinero, self._price_kill)
    	  return False
    	  cursor.close()

    def cmd_teleport(self, data, client, cmd=None):
      if(client.maxLevel > 100):
        input = self._adminPlugin.parseUserCmd(data)
        sclient = self._adminPlugin.findClientPrompt(input[0], client)
        self.console.write("teleport %s %s" % (client.cid, sclient.cid))
      else:
    	  q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
    	  cursor = self.console.storage.query(q)
    	  r = cursor.getRow()
    	  iduser = r['iduser']
    	  dinero = r['dinero']
    	  idioma = r['idioma']
    	  input = self._adminPlugin.parseUserCmd(data)
    	  if not data:
    	  	client.message('^7Type !teleport ^5<^2player^5>')
    	  	return False
    	  sclient = self._adminPlugin.findClientPrompt(input[0], client)
    	  if not sclient: return False
    	  if (dinero > self._price_teleport):
    	    if((client.team == b3.TEAM_BLUE) == (sclient.team == b3.TEAM_BLUE)) or ((client.team == b3.TEAM_RED) == (sclient.team == b3.TEAM_RED)):
              if client.cid == sclient.cid:
                client.message('^7You cant teleport to you ! ^2[^1GAY^2]')
              else:
    	        q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (self._price_teleport, client.id))
    	        self.console.storage.query(q)
    	        self.console.write("teleport %s %s" % (client.cid, sclient.cid))
    	        client.message('^7you teleport to [%s]' % (sclient.exactName))
    	      return True
    	    else:
    	    	client.message('^7You can only teleport to ^5[^6Friends^5]')
    	    	return False
    	  else:
    	  	client.message('^6You Dont have coins. ^7Your money is: ^5[^6%s^5] ^7and you need ^5[^2%s^5]^7 more to teleport' % (dinero, self._price_teleport))
    	  return False
    	  cursor.close()
    def cmd_givemoney(self, data, client, cmd=None):
      input = self._adminPlugin.parseUserCmd(data)
      sclient = self._adminPlugin.findClientPrompt(input[0], client)
      q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
      cursor = self.console.storage.query(q)
      r = cursor.getRow()
      iduser = r['iduser']
      dinero = r['dinero']
      idioma = r['idioma']
      input = self._adminPlugin.parseUserCmd(data)
      if not data:
			client.message('^7Type !givemoney ^5<^2player^5>')
			return False
      else:
        sclient = self._adminPlugin.findClientPrompt(input[0], client)
        if not sclient: return False
        else:
    	  q=('UPDATE `dinero` SET `dinero` = dinero+50000 WHERE iduser = "%s"' % (sclient.id))
    	  self.console.storage.query(q)
    	  client.message('^7you give 50000 coins to ^2[^7%s^2]' % (sclient.exactName))
    	return True
        cursor.close()

    def cmd_god(self, data, client, cmd=None):
      if(client.maxLevel > 100):
        input = self._adminPlugin.parseUserCmd(data)
        sclient = self._adminPlugin.findClientPrompt(input[0], client)
        self.console.write("sv_cheat 1")
        self.console.write("spoof %s god" % (sclient.cid))
        self.console.write("sv_cheat 0")
      else:
    	  q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
    	  cursor = self.console.storage.query(q)
    	  r = cursor.getRow()
    	  iduser = r['iduser']
    	  dinero = r['dinero']
    	  idioma = r['idioma']
    	  input = self._adminPlugin.parseUserCmd(data)
    	  if not data:
    	  	client.message('^7Type !god ^5<^2player^5>')
    	  	return False
    	  sclient = self._adminPlugin.findClientPrompt(input[0], client)
    	  if not sclient: return False
    	  if (dinero > 7500):
    	    if((client.team == b3.TEAM_BLUE) == (sclient.team == b3.TEAM_BLUE)) or ((client.team == b3.TEAM_RED) == (sclient.team == b3.TEAM_RED)):
    	      q=('UPDATE `dinero` SET `dinero` = dinero-%s WHERE iduser = "%s"' % (self._price_god, client.id))
    	      self.console.storage.query(q)
              self.console.say("^6[!]^7%s ^7buy god to %s ^2[^51 minut^2] ^6[!] ^6[Commands BLOCKED]" % (client.exactName, sclient.exactName))
              self.console.write("tivmodON 1")
              self.console.write("spoof %s god" % (sclient.cid))
              self.console.write("tivmodOFF 1")
              time.sleep(32)
              self.console.say("^1[!]^732 seconds and ^2[^7%s^2]^7 -> ^2[^7GOD^2] ^7finish^1[!] ^6[Commands BLOCKED]" % (sclient.exactName))
              time.sleep(32)
              self.console.write("tivmodON 1")
              self.console.write("spoof %s god" % (sclient.cid))
              self.console.write("tivmodOFF 1")
              self.console.say("^2[!]^7%s is not god now ^2[!] ^5You can kill him ^2[!]" % (sclient.exactName))
    	      return True
    	    else:
    	    	client.message('^7Only ^5[^6Friends^5]^7 can god')
    	    	return False
    	  else:
    	  	client.message('^6You Dont have coins. ^7Your coins are ^5[^6%s^5] ^7and you need ^5[^27500^5]^7 to give GOD 1 minut' % dinero)
    	  return False
    	  cursor.close()
    def cmd_buy(self, data, client, cmd=None):
        q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
        cursor = self.console.storage.query(q)
        r = cursor.getRow()
        idioma = r['idioma']
        if client.team == b3.TEAM_BLUE:
            self.console.write('tell %s ^7[^2!god <player>(!gd)^7]^7 / ^7[^5Invincible^7] ^7/ Price ^2[^6%s^2]' % (client.cid, self._price_god))
            self.console.write('tell %s ^7[^2!kill <player>(!kl)^7]^7 / ^7[^5Kill an enemy^7] ^7/ Price ^2[^6%s^2]' % (client.cid, self._price_kill))
            self.console.write('tell %s ^7[^2!teleport <player>(!tp)^7]^7 / ^7[^5Teleport to a friend^7] ^7/ Price ^2[^6%s^2]' % (client.cid, self._price_teleport))
            self.console.write('tell %s ^7[^2!money <player>(!mo)^7]^7 / ^7[^5See money^7] ^7/ Price ^2[^6?^2]' % (client.cid))
            self.console.write('tell %s ^7[^2!level <player>(!lvl)^7]^7 / ^7[^5See level^7] ^7/ Price ^2[^6?^2]' % (client.cid))
            return True
        if client.team == b3.TEAM_RED:
            self.console.write('tell %s ^7[^2!god <player>(!gd)^7]^7 / ^7[^5Invincible^7] ^7/ Price ^2[^6%s^2]' % (client.cid, self._price_god))
            self.console.write('tell %s ^7[^2!kill <player>(!kl)^7]^7 / ^7[^5Kill an enemy^7] ^7/ Price ^2[^6%s^2]' % (client.cid, self._price_kill))
            self.console.write('tell %s ^7[^2!teleport <player>(!tp)^7]^7 / ^7[^5Teleport to a friend^7] ^7/ Price ^2[^6%s^2]' % (client.cid, self._price_teleport))
            self.console.write('tell %s ^7[^2!money <player>(!mo)^7]^7 / ^7[^5See money^7] ^7/ Price ^2[^6?^2]' % (client.cid))
            self.console.write('tell %s ^7[^2!level <player>(!lvl)^7]^7 / ^7[^5See level^7] ^7/ Price ^2[^6?^2]' % (client.cid))
            return True
    def cmd_moneyhelp(self, data, client, cmd=None):
        q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
        cursor = self.console.storage.query(q)
        r = cursor.getRow()
        idioma = r['idioma']
        if client.team == b3.TEAM_BLUE:
            self.console.write('tell %s %s' % (client.cid, self._message_help))
            return True
        if client.team == b3.TEAM_RED:
            self.console.write('tell %s %s' % (client.cid, self._message_help))
            return True
    def cmd_topmoney(self, data, client, cmd=None, ext=False):
	 """\
	 - Displays the richest players
	 """
	 dinero = 'dinero'
	 thread.start_new_thread(self.getTopMoney, (client, cmd, ext, dinero))
	 return
    def getTopMoney(self, client, cmd, ext, prestige):
      q=('SELECT * FROM `dinero` WHERE (`dinero` > 0) ORDER BY `dinero` DESC LIMIT 3')
      cursor = self.console.storage.query(q)
      r = cursor.getRow()
      self.debug(q)
      cursor = self.query(q)
      if cursor and (cursor.rowcount > 0):
        message = ('^6[ ^3[^2Top^3] ^7rich player ^6]')
        if ext:
            self.console.say(message)
        else:
           cmd.sayLoudOrPM(client, message)
        c = 1
        while not cursor.EOF:
            r = cursor.getRow()
            dinero = r['dinero']
            message = '^3[^2#%s^3]^7:^3@%s^7>%s^6[^7coins: ^2%s^6]' % (
                c, r['iduser'], r['firstname'], r['dinero'])
            if ext:
                self.console.say(message)
            else:
                cmd.sayLoudOrPM(client, message)
            cursor.moveNext()
            c += 1
            time.sleep(1)
      else:
		message = 'No maps have been %sd yet!' % dinero[:-1]
		if ext:
			self.console.say(message)
		else:
			cmd.sayLoudOrPM(client, message)
		return None
      return 
    def cmd_givexp(self, data, client, cmd=None):
      input = self._adminPlugin.parseUserCmd(data)
      sclient = self._adminPlugin.findClientPrompt(input[0], client)
      q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
      cursor = self.console.storage.query(q)
      r = cursor.getRow()
      iduser = r['iduser']
      expPoints = r['expPoints']
      input = self._adminPlugin.parseUserCmd(data)
      if not data:
			client.message('^7Type !giveexp ^5<^2player^5>')
			return False
      else:
        sclient = self._adminPlugin.findClientPrompt(input[0], client)
        if not sclient: return False
        else:
    	  q=('UPDATE `dinero` SET `expPoints` = expPoints+1000 WHERE iduser = "%s"' % (sclient.id))
    	  self.console.storage.query(q)
    	  client.message('^7You give 1000 exppoints to ^2[^7%s^2]' % (sclient.exactName))
    	return True
        cursor.close()
    def cmd_pay(self, data, client, cmd=None):
      """\
      Now you can pay your friend. Use !pay <player> <number>
      """
      input = self._adminPlugin.parseUserCmd(data)
      sclient = self._adminPlugin.findClientPrompt(input[0], client)
      q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
      cursor = self.console.storage.query(q)
      r = cursor.getRow()
      iduser = r['iduser']
      dinero = r['dinero']
      input = self._adminPlugin.parseUserCmd(data)
      number = int(input[1])
      if not data:
			client.message('^7Type !pay ^5<^2player^5> <number>')
			return False
      if not number:
			client.message('^7Type !pay ^5<^2player^5> <number>')
			return False
      else:
        sclient = self._adminPlugin.findClientPrompt(input[0], client)
        if not sclient: return False
        else:
          if number < dinero:
            if number > 0:
    	      q=('UPDATE `dinero` SET `dinero` = dinero + %s WHERE iduser = "%s"' % (number, sclient.id))
    	      self.console.storage.query(q)
    	      q=('UPDATE `dinero` SET `dinero` = dinero - %s WHERE iduser = "%s"' % (number,  client.id))
    	      self.console.storage.query(q)
    	      client.message('^7You pay %s coins to ^2[^7%s^2]' % (number, sclient.exactName))
            else:
              client.message('^1You need to pay more money.')
          else:
            client.message('^1You need more money!')
    	return True
        cursor.close()
    def deconnection(self, client, target, data=None):
    	  if client:
    	    q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
    	    cursor = self.console.storage.query(q)
    	    r = cursor.getRow()
    	    iduser = r['iduser']
            expPoints = r['expPoints']
            statsbonnuskills = r['statsbonnuskills']
            level = r['level']
            dinero = r['dinero']
            multiplier = r['multiplier']
            prestige = r['prestige']
            totalexpPoints = r['totalexpPoints']
## FOR KILL !
    	    if(client.team == b3.TEAM_RED) or (client.team == b3.TEAM_BLUE):
              q=('UPDATE `dinero` SET `enligne` = enligne-1 WHERE iduser = "%s"' % (client.id))
              self.console.storage.query(q)
              cursor.close()
    def connection(self, client, target, data=None):
    	  if client:
    	    q=('SELECT * FROM `dinero` WHERE `iduser` = "%s"' % (client.id))
    	    cursor = self.console.storage.query(q)
    	    r = cursor.getRow()
    	    iduser = r['iduser']
            expPoints = r['expPoints']
            statsbonnuskills = r['statsbonnuskills']
            level = r['level']
            dinero = r['dinero']
            multiplier = r['multiplier']
            prestige = r['prestige']
            totalexpPoints = r['totalexpPoints']
## FOR KILL !
    	    if(client.team == b3.TEAM_RED) or (client.team == b3.TEAM_BLUE):
              q=('UPDATE `dinero` SET `enligne` = enligne+1 WHERE iduser = "%s"' % (client.id))
              self.console.storage.query(q)
              cursor.close()