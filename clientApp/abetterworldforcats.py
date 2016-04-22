from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.config import Config
from functools import partial
import firebase
import time

############################################################
#                       importing widgets
############################################################
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image

############################################################
#                       database setup                
############################################################
url = "https://shinglez.firebaseio.com"
token = "LMM5MC2Q6G1wCDrbrOMraGETVPCj6CSKBpUS2RtQ"
firebase = firebase.FirebaseApplication(url,token)
############################################################
#                       Screen design                 
############################################################
Config.set('graphics', 'width', '360') 
Config.set('graphics', 'height', '640')
Builder.load_file('./abetterworldforcats.kv')

############################################################
#                       App functionalities                 
############################################################
class login_screen(Screen):
	def log_in(self):
		self.ids['status'].text=''
		entered_name = self.ids['username'].text.strip()
		entered_password = self.ids['password'].text
		if entered_name not in firebase.get('/users'):
			self.ids['status'].text = "User doesn't exists!"
		else:
			if entered_password == firebase.get('/users')[entered_name]['password']:
				self.manager.get_screen('profile').user = entered_name
				self.manager.get_screen('profile').display_data()
				self.manager.current = 'profile'
			else:
				self.ids['status'].text = 'Password incorrect!'

class signup_screen(Screen):
	def email_availability(self, email):
		for user in firebase.get('/users'):
			if email == firebase.get('/users/'+user+'/email'):
				return False
		else:
			return True

	def sign_me_up(self):
		entered_username = self.ids['username'].text.strip()
		entered_email = self.ids['email'].text.strip()
		entered_password = self.ids['password'].text.strip()
		confirm_password = self.ids['password_confirm'].text.strip()
		if " " in entered_username or "	" in entered_username:
			self.ids['status'].text = 'Username invalid! Cannot have spaces'
		elif entered_username in firebase.get('/users'):
			self.ids['status'].text = 'Username Taken!'
		elif self.email_availability(entered_email) == False:
			self.ids['status'].text = 'Email has already been signed up!'
		elif len(entered_password) < 7:
			self.ids['status'].text = "Password too short!"
		elif entered_password != confirm_password:
			self.ids['status'].text = 'Password mismatched!'
		else:
			user = {'dispensers': ['None'], 'email': entered_email, 'password': entered_password, 'pic_url': 'http://i.imgur.com/VMtRJHG.jpg', 'badges': ['None']}
			firebase.put('/', '/users/'+entered_username, user)
			self.ids['sign_up'].clear_widgets()
			self.ids['sign_up'].add_widget(Label(text="Sign Up Successful!"))
			self.ids['sign_up'].add_widget(Label(text="Start contributing to a better world for cats!"))
			self.ids['sign_up'].add_widget(Button(text='Go to your profile', color=(0,0,0,1), background_normal='./assets/buttons/long_button.png', background_down='./assets/buttons/long_button_down.png', on_press=self.transfer_data))

	def transfer_data(self, instance):
		self.manager.get_screen('profile').user = self.ids['username'].text.strip()
		self.manager.get_screen('profile').display_data()
		self.manager.transition.direction = 'left'
		self.manager.current = 'profile'

class profile_screen(Screen):
	def display_data(self):
		self.ids['user'].text = self.user
		self.ids['email'].text = firebase.get('/users')[self.user]['email']
		self.ids['pic'].source = firebase.get('/users')[self.user]['pic_url']
	def transfer_data(self):
		self.manager.get_screen('dispenser_screen').user = self.user
		self.manager.get_screen('dispenser_screen').ids['dispensers_manager'].clear_widgets()
		self.manager.get_screen('dispenser_screen').generate_screen()
	def to_contact_form(self):
		self.manager.get_screen('contact_form').generate_form()
		self.manager.get_screen('contact_form').prev_screen = 'profile'
		self.manager.transition.direction = 'left'
		self.manager.current = 'contact_form'
	def to_badges(self):
		self.manager.get_screen('badges').ids['badges_display'].clear_widgets()
		self.manager.get_screen('badges').display_badges()
		self.manager.transition.direction = 'left'
		self.manager.current = 'badges'

class dispenser_screen(Screen):
	def generate_screen(self):
		self.dispensers = firebase.get('/users')[self.user]['dispensers']
		self.ids['dispensers_manager'].add_widget(Button(text='<< Back to Profile',color=(0,0,0,1), background_normal='./assets/buttons/long_button.png', background_down='./assets/buttons/long_button_down.png', on_press=self.change_to_profile))
		if len(self.dispensers) == 1:
			self.ids['dispensers_manager'].add_widget(Label(text="You don't have any dispenser!", color=(0,0,0,1)))
			self.ids['dispensers_manager'].add_widget(Label(text="Add Now?", color=(0,0,0,1)))
		else:
			for i in xrange(1, len(self.dispensers)):
				a_dispenser = Button(text=self.dispensers[i], color=(0,0,0,1), background_normal='./assets/buttons/dis_button.png', background_down='./assets/buttons/dis_button_down.png', size_hint=(0.906, 1), on_press=partial(self.go_to_status, i))
				delete_button = Button(size_hint=(0.094, 1), background_normal='./assets/buttons/delete.png', background_down='./assets/buttons/delete.png', on_press=partial(self.delete_dispenser, i))
				box = BoxLayout()
				box.add_widget(a_dispenser)
				box.add_widget(delete_button)
				self.ids['dispensers_manager'].add_widget(box)
			self.ids['dispensers_manager'].add_widget(Label())
		self.ids['dispensers_manager'].add_widget(Button(text="Add New Dispenser",color=(0,0,0,1), background_normal='./assets/buttons/long_button.png', background_down='./assets/buttons/long_button_down.png', on_press=self.change_to_add))
		self.ids['dispensers_manager'].add_widget(Button(text="Buy New Dispenser",color=(0,0,0,1), background_normal='./assets/buttons/long_button.png', background_down='./assets/buttons/long_button_down.png', on_press=self.change_to_buy))

	def go_to_status(self, dispenser_number, instance):
		self.manager.get_screen('dispenser_status').dispenser_name = self.dispensers[dispenser_number]
		self.manager.get_screen('dispenser_status').generate_screen()
		self.manager.transition.direction = 'left'
		self.manager.current = 'dispenser_status'

	def delete_dispenser(self, dispenser_number, instance):
		self.dispensers.remove(self.dispensers[dispenser_number])
		firebase.put('/', '/users/'+self.user+'/dispensers', self.dispensers)
		self.ids['dispensers_manager'].clear_widgets()
		self.generate_screen()

	def change_to_add(self, instance):
		self.manager.get_screen('add_dispenser').ids['search_result'].clear_widgets()
		self.manager.transition.direction = 'left'
		self.manager.current = 'add_dispenser'
	def change_to_buy(self, instance):
		self.manager.transition.direction = 'left'
		self.manager.current = 'req_dispenser'
	def change_to_profile(self, instance):
		self.manager.transition.direction = 'right'
		self.manager.current = 'profile'

class dispenser_status(Screen):
	def generate_screen(self):
		dispenser = firebase.get('/dispensers/'+self.dispenser_name)
		if dispenser['fullness'] == 100:
			self.ids['status_img'].source = './assets/percentage/100.png'
		elif dispenser['fullness'] == 75:
			self.ids['status_img'].source = './assets/percentage/75.png'
		elif dispenser['fullness'] == 50:
			self.ids['status_img'].source = './assets/percentage/50.png'
		elif dispenser['fullness'] == 25:
			self.ids['status_img'].source = './assets/percentage/25.png'
		elif dispenser['fullness'] == 0:
			self.ids['status_img'].source = './assets/percentage/0.png'
		self.ids['dispenser_name'].text = self.dispenser_name
		self.ids['last_fill'].text = 'Last filled at: '+dispenser['last_filled']

class add_dispenser(Screen):
	def search_by_name(self):
		self.search_result = []
		self.user = self.manager.get_screen('profile').user
		user_search = self.ids['search_box'].text
		for dispenser in firebase.get('/dispensers'):
			if user_search in dispenser:
				if firebase.get('/dispensers/'+dispenser)['accessability']=="public" or self.user in firebase.get('/dispensers/'+dispenser)['accessability']:
					self.search_result.append(dispenser)
		self.display_result()

	def search_by_zip(self):
		self.search_result = []
		self.user = self.manager.get_screen('profile').user
		user_search = self.ids['search_box'].text
		for dispenser in firebase.get('/dispensers'):
			if user_search.isdigit():
				if firebase.get('/dispensers/'+dispenser)['location']==int(user_search):
					self.search_result.append(dispenser)
		self.display_result()

	def display_result(self):
		self.ids['search_result'].clear_widgets()
		for i in xrange(0,3):
			self.ids['search_result'].add_widget(BoxLayout())
		if len(self.search_result)==0:
			self.ids['search_result'].add_widget(Label(text="Cannot find any dispenser!", color=(0,0,0,1)))
		else:	
			for dispenser in self.search_result:
				box = BoxLayout()
				box.add_widget(Label(text=dispenser, size_hint=(0.817, 1), color=(0,0,0,1)))
				add_button=Button(id=dispenser, size_hint=(0.083, 1))
				if dispenser in firebase.get('/users/'+self.manager.get_screen('profile').user)['dispensers']:
					add_button.background_normal='./assets/buttons/checked.png'
					add_button.background_down='./assets/buttons/checked.png'
				else:
					add_button.background_normal='./assets/buttons/add.png'
					add_button.background_down='./assets/buttons/add.png'
					add_button.bind(on_press=self.add_the_dispenser)
				box.add_widget(add_button)
				box.add_widget(Label(size_hint=(0.1, 1)))
				self.ids['search_result'].add_widget(box)

	def add_the_dispenser(self, instance):
		user_dispensers = firebase.get('/users/'+self.user+'/dispensers')
		user_dispensers.append(instance.id)
		firebase.put('/', '/users/'+self.user+'/dispensers', user_dispensers)
		self.display_result()

	def to_dispenser_manager(self):
		self.manager.get_screen('dispenser_screen').ids['dispensers_manager'].clear_widgets()
		self.manager.get_screen('dispenser_screen').generate_screen()
		self.manager.transition.direction = 'right'
		self.manager.current = 'dispenser_screen'

class req_dispenser(Screen):
	def to_contact_form(self):
		self.manager.get_screen('contact_form').generate_form()
		self.manager.get_screen('contact_form').prev_screen = 'req_dispenser'
		self.manager.transition.direction = 'left'
		self.manager.current = 'contact_form'
	def to_checkout(self):
		self.manager.get_screen('checkout').generate_screen()
		self.manager.transition.direction = 'left'
		self.manager.current = 'checkout'

class contact_form(Screen):
	def generate_form(self):
		self.ids['box'].clear_widgets()
		self.ids['form'].clear_widgets()
		self.ids['form'].add_widget(Button(text='<< Back',color=(0,0,0,1), background_normal='./assets/buttons/long_button.png', background_down='./assets/buttons/long_button_down.png', on_press=self.back))
		self.ids['form'].add_widget(BoxLayout())
		self.ids['form'].add_widget(BoxLayout())
		self.ids['form'].add_widget(BoxLayout())
		self.ids['form'].add_widget(BoxLayout())
		self.ids['form'].add_widget(BoxLayout())
		self.query = TextInput()
		self.ids['box'].add_widget(BoxLayout())
		self.ids['box'].add_widget(self.query)
		self.ids['form'].add_widget(Button(text='Submit',color=(0,0,0,1), background_normal='./assets/buttons/long_button.png', background_down='./assets/buttons/long_button_down.png', on_press=self.submit))
	def submit(self, instance):
		queries = firebase.get('/queries')
		user = self.manager.get_screen('profile').user
		the_time = time.ctime()
		text = self.query.text
		the_query = {'who': user, "time": the_time, "query": text}
		queries.append(the_query)
		firebase.put('/', '/queries', queries)
		self.ids['box'].clear_widgets()
		self.ids['form'].clear_widgets()
		self.ids['form'].add_widget(Button(text='<< Back',color=(0,0,0,1), background_normal='./assets/buttons/long_button.png', background_down='./assets/buttons/long_button_down.png', on_press=self.back))
		self.ids['form'].add_widget(BoxLayout())
		self.ids['form'].add_widget(BoxLayout())
		self.ids['form'].add_widget(Label(text="Thanks! We'll get back to you asap", color=(0,0,0,1)))
	def back(self, instance):
		self.manager.transition.direction='right'
		self.manager.current = self.prev_screen


class checkout(Screen):
	def generate_screen(self):
		self.ids['order'].clear_widgets()
		self.ids['order'].add_widget(BoxLayout())
		self.ids['order'].add_widget(Label(text='Credit Card Info', color=(0,0,0,1)))
		box = BoxLayout()
		box.add_widget(Label(text='Number', size_hint=(0.3, 1), color=(0,0,0,1)))
		self.cred_number=TextInput(size_hint=(0.7, 1), multiline=False)
		box.add_widget(self.cred_number)
		self.ids['order'].add_widget(box)
		box2 = BoxLayout()
		box2.add_widget(Label(text='CCV', size_hint=(0.3, 1), color=(0,0,0,1)))
		self.ccv=TextInput(size_hint=(0.3,1), multiline=False, password=True)
		box2.add_widget(self.ccv)
		box2.add_widget(Label(size_hint=(0.4,1)))
		self.ids['order'].add_widget(box2)
		self.ids['order'].add_widget(Label(text='Personal Info', color=(0,0,0,1)))
		box3 = BoxLayout()
		box3.add_widget(Label(text='Full name', size_hint=(0.3, 1), color=(0,0,0,1)))
		self.the_name = TextInput(size_hint=(0.7, 1), multiline=False)
		box3.add_widget(self.the_name)
		self.ids['order'].add_widget(box3)
		box4 = BoxLayout()
		box4.add_widget(Label(text='Phone Number', size_hint=(0.3, 1), color=(0,0,0,1)))
		self.hp_no = TextInput(size_hint=(0.7, 1), multiline=False)
		box4.add_widget(self.hp_no)
		self.ids['order'].add_widget(box4)
		self.ids['order'].add_widget(Button(text='Submit',color=(0,0,0,1), background_normal='./assets/buttons/long_button.png', background_down='./assets/buttons/long_button_down.png', on_press=self.place_order))
	def place_order(self, instance):
		user = self.manager.get_screen('profile').user
		cred_number = self.cred_number.text
		ccv = self.ccv.text
		name = self.the_name.text
		hp = self.hp_no.text
		orders = firebase.get('/orders')
		the_order = {'user': user, 'creditcard': cred_number, 'ccv': ccv, 'name': name, 'phone': hp}
		orders.append(the_order)
		firebase.put('/', '/orders', orders)
		self.ids['order'].clear_widgets()
		self.ids['order'].add_widget(BoxLayout())
		self.ids['order'].add_widget(Label(text="Thanks for purchasing our product!", color=(0,0,0,1)))
		self.ids['order'].add_widget(Label(text="Please find your receipt in your email", color=(0,0,0,1)))



class settings(Screen):
	def to_picture(self):
		self.manager.get_screen('update_pic').ids['status'].text = "URL of your public photo, imgur.com recommended"
		self.manager.get_screen('update_pic').ids['input'].text = ""
		self.manager.transition.direction = 'left'
		self.manager.current = 'update_pic'
	def to_email(self):
		self.manager.get_screen('update_email').ids['status'].text = "Type in your new email"
		self.manager.get_screen('update_email').ids['input'].text = ""
		self.manager.transition.direction = 'left'
		self.manager.current = 'update_email'
	def to_password(self):
		self.manager.get_screen('update_password').ids['status'].text = ""
		self.manager.transition.direction = 'left'
		self.manager.current = 'update_password'

class update_pic(Screen):
	def update(self):
		user = self.manager.get_screen('profile').user
		pic_url = self.ids['input'].text
		firebase.put('/', '/users/'+user+'/pic_url', pic_url)
		self.manager.get_screen('profile').ids['pic'].source = pic_url
		self.ids['status'].text = "Successfully update profile picture!"

class update_email(Screen):
	def update(self):
		user = self.manager.get_screen('profile').user
		email = self.ids['input'].text
		firebase.put('/', '/users/'+user+'/email', email)
		self.manager.get_screen('profile').ids['email'].text = email
		self.ids['status'].text = "Successfully update your email!"

class update_password(Screen):
	def submit(self):
		new_password = self.ids['new_password'].text
		old_password = self.ids['old_password'].text
		confirm = self.ids['confirm'].text
		password = firebase.get('/users/'+self.manager.get_screen('profile').user+'/password')
		if old_password == password:
			if len(new_password) > 7:
				if new_password == confirm:
					firebase.put('/', '/users/'+self.manager.get_screen('profile').user+'/password', new_password)
					self.ids['new_password'].text = ""
					self.ids['old_password'].text = ""
					self.ids['confirm'].text = ""
					self.ids['status'].text = "Password updated!"
				else:
					self.ids['status'].text = "New password mismatched!"
			else:
				self.ids['status'].text = "New password too short!"
				print len(new_password)
		else:
			self.ids['status'].text = "Incorrect password!"

class badges(Screen):
	def display_badges(self):
		badges = firebase.get('/users/'+self.manager.get_screen('profile').user+'/badges')
		badges.remove("None")
		badges_tag={'add': 'add', 'status':'status', 'log':'log', 'buy':'buy', '5':'5', 'join':'join'}
		if len(badges)==0:
			self.ids['badges_display'].add_widget(BoxLayout())
			self.ids['badges_display'].add_widget(Label(text="You don't have any badge yet!", color=(0,0,0,1)))
			self.ids['badges_display'].add_widget(Label(text="Be more active!", color=(0,0,0,1)))
		else:
			i = 0
			image_box=BoxLayout()
			name_box=BoxLayout()
			while i<len(badges):
				if i%3==0:
					self.ids['badges_display'].add_widget(image_box)
					self.ids['badges_display'].add_widget(name_box)
					for j in xrange(0,3):
						self.ids['badges_display'].add_widget(BoxLayout())
					image_box=BoxLayout()
					name_box=BoxLayout()
				image_box.add_widget(Image(source='./assets/badges/'+badges[i]+'.png', size_hint=(1,4)))
				name_box.add_widget(Label(text="[["+badges_tag[badges[i]]+"]]", color=(0,0,0,1)))
				i+=1
			self.ids['badges_display'].add_widget(image_box)
			self.ids['badges_display'].add_widget(name_box)
############################################################
#                       Main App              
############################################################
class a_better_world_for_cats(App):
	def build(self):
		sm = ScreenManager()
		sm.add_widget(login_screen(name='login'))
		sm.add_widget(profile_screen(name='profile'))
		sm.add_widget(dispenser_screen(name='dispenser_screen'))
		sm.add_widget(badges(name='badges'))
		sm.add_widget(settings(name='settings'))
		sm.add_widget(update_pic(name='update_pic'))
		sm.add_widget(update_email(name='update_email'))
		sm.add_widget(update_password(name='update_password'))
		sm.add_widget(signup_screen(name='signup'))
		sm.add_widget(dispenser_status(name='dispenser_status'))
		sm.add_widget(add_dispenser(name='add_dispenser'))
		sm.add_widget(req_dispenser(name='req_dispenser'))
		sm.add_widget(contact_form(name='contact_form'))
		sm.add_widget(checkout(name='checkout'))
		sm.current='login'
		return sm

if __name__ == '__main__':
	a_better_world_for_cats().run()