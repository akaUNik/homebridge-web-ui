# -*- coding: utf-8 -*-
"""
	homerbidge web ui
"""
import time                       
import json                                              
from itertools import cycle                                                     
from flask import Flask, render_template, request, jsonify         
#import os                         
import subprocess

app = Flask(__name__)                                                           
switches = []
states = {}

# switch 1
# name = 'LED'
# on_cmd = 'timeout 1s broadlinktools.py --cmd=togglestate --ip=192.168.0.12 --mac=34:EA:34:BD:38:8A'
# off_cmd = 'timeout 1s broadlinktools.py --cmd=togglestate --ip=192.168.0.12 --mac=34:EA:34:BD:38:8A'
# state_cmd = 'timeout 1s broadlinktools.py --cmd=getstate --ip=192.168.0.12 --mac=34:EA:34:BD:38:8A'

with open('/var/homebridge/config.json') as config_file:
	config = json.load(config_file)  
	for p in config['platforms']:
		if p['platform'] == 'cmdSwitch2':
			switches = p['switches']
			#print(switches)

# fix switch names
for s in switches:
	s['name'] = s['name'].replace('@', '-at-')


def _exec(cmd):
	ret = subprocess.call(cmd, shell=True)
	return ret

def _get_states():
	for s in switches:
		state = 'na'
		if s.get('state_cmd', '') != '':
			ret = _exec(s['state_cmd'])
			state = 'on' if ret == 0 else 'off'
			#print s['name'], ret, state
		states.update({s['name']: state})
	#print(states)
	return states

def _switch_on(switch):
	switch.replace('-at-', '@')
	for s in switches:
		if s['name'] == switch:
			_exec(s['on_cmd'])

def _switch_off(switch):
	switch.replace('-at-', '@')
	for s in switches:
		if s['name'] == switch:
			_exec(s['off_cmd'])

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/get_states')
def get_states():
	states = _get_states()
	return jsonify(states=states)

@app.route('/press_btn')
def press_btn():
	switch = request.args.get('switch')
	cmd = request.args.get('cmd')

	if cmd == 'switch_on':
		_switch_on(switch)
		return jsonify(switch=switch, state='on')
	elif cmd == 'switch_off':
		_switch_off(switch)
		return jsonify(switch=switch, state='off')
	return jsonify(result='Unknown command')

if __name__ == "__main__":                                                      
    app.run(host='0.0.0.0', port=5000)