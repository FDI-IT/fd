#!/usr/bin/python

import cgi
import re

ss_form_name = """
				<li>
					<span class="contact-label">
						<label for="ss-form-name">
							Name *
						</label>
					</span>
					<span class="contact-input">
						<input type="text" name="ss-form-name" id="ss-form-name" value="">
					</span>
				</li>
"""
ss_form_title = """				
				<li>
					<span class="contact-label">
						<label for="ss-form-title">
							Title
						</label>
					</span>
					<span class="contact-input">
						<input type="text" name="ss-form-title" id="ss-form-title" value="">
					</span>
				</li>
"""
ss_form_email = """				
				<li>
					<span class="contact-label">
						<label for="ss-form-email">
							E-Mail *
						</label>
					</span>
					<span class="contact-input">
						<input type="text" name="ss-form-email" id="ss-form-email" value="">
					</span>
				</li>
"""
ss_form_phone = """						
				<li>
					<span class="contact-label">
						<label for="ss-form-phone">
							Phone *
						</label>
					</span>
					<span class="contact-input">
						<input type="text" name="ss-form-phone" id="ss-form-phone" value="">
					</span>
				</li>
"""
ss_form_company = """						
				<li>
					<span class="contact-label">
						<label for="ss-form-company">
							Company *
						</label>
					</span>
					<span class="contact-input">
						<input type="text" name="ss-form-company" id="ss-form-company" value="">
					</span>
				</li>
"""
ss_form_address = """						
				<li>
					<span class="contact-label">
						<label for="ss-form-address">
							address *
						</label>
					</span>
					<span class="contact-input">
						<input type="text" name="ss-form-address" id="ss-form-address" value="">
					</span>
				</li>
"""
ss_form_city = """					
				<li>
					<span class="contact-label">
						<label for="ss-form-city">
							City *
						</label>
					</span>
					<span class="contact-input">
						<input type="text" name="ss-form-city" id="ss-form-city" value="">
					</span>
				</li>
"""
ss_form_state = """						
				<li>
					<span class="contact-label">
						<label for="ss-form-state">
							State *
						</label>
					</span>
					<span class="contact-input">
						<input type="text" name="ss-form-state" id="ss-form-state" value="">
					</span>
				</li>
"""
ss_form_zip = """						
				<li>
					<span class="contact-label">
						<label for="ss-form-zip">
							Zip Code *
						</label>
					</span>
					<span class="contact-input">
						<input type="text" name="ss-form-zip" id="ss-form-zip" value="">
					</span>
				</li>
"""
ss_form_country = """						
				<li>
					<span class="contact-label">
						<label for="ss-form-country">
							Country *
						</label>
					</span>
					<span class="contact-select">
						<select name="ss-form-country" id="ss-form-country"> 
							<option value="" selected="selected">Please select country...</option> 
							<option value="United States">United States</option> 
							<option value="United Kingdom">United Kingdom</option> 
							<option value="Afghanistan">Afghanistan</option> 
							<option value="Albania">Albania</option> 
							<option value="Algeria">Algeria</option> 
							<option value="American Samoa">American Samoa</option> 
							<option value="Andorra">Andorra</option> 
							<option value="Angola">Angola</option> 
							<option value="Anguilla">Anguilla</option> 
							<option value="Antarctica">Antarctica</option> 
							<option value="Antigua and Barbuda">Antigua and Barbuda</option> 
							<option value="Argentina">Argentina</option> 
							<option value="Armenia">Armenia</option> 
							<option value="Aruba">Aruba</option> 
							<option value="Australia">Australia</option> 
							<option value="Austria">Austria</option> 
							<option value="Azerbaijan">Azerbaijan</option> 
							<option value="Bahamas">Bahamas</option> 
							<option value="Bahrain">Bahrain</option> 
							<option value="Bangladesh">Bangladesh</option> 
							<option value="Barbados">Barbados</option> 
							<option value="Belarus">Belarus</option> 
							<option value="Belgium">Belgium</option> 
							<option value="Belize">Belize</option> 
							<option value="Benin">Benin</option> 
							<option value="Bermuda">Bermuda</option> 
							<option value="Bhutan">Bhutan</option> 
							<option value="Bolivia">Bolivia</option> 
							<option value="Bosnia and Herzegovina">Bosnia and Herzegovina</option> 
							<option value="Botswana">Botswana</option> 
							<option value="Bouvet Island">Bouvet Island</option> 
							<option value="Brazil">Brazil</option> 
							<option value="British Indian Ocean Territory">British Indian Ocean Territory</option> 
							<option value="Brunei Darussalam">Brunei Darussalam</option> 
							<option value="Bulgaria">Bulgaria</option> 
							<option value="Burkina Faso">Burkina Faso</option> 
							<option value="Burundi">Burundi</option> 
							<option value="Cambodia">Cambodia</option> 
							<option value="Cameroon">Cameroon</option> 
							<option value="Canada">Canada</option> 
							<option value="Cape Verde">Cape Verde</option> 
							<option value="Cayman Islands">Cayman Islands</option> 
							<option value="Central African Republic">Central African Republic</option> 
							<option value="Chad">Chad</option> 
							<option value="Chile">Chile</option> 
							<option value="China">China</option> 
							<option value="Christmas Island">Christmas Island</option> 
							<option value="Cocos (Keeling) Islands">Cocos (Keeling) Islands</option> 
							<option value="Colombia">Colombia</option> 
							<option value="Comoros">Comoros</option> 
							<option value="Congo">Congo</option> 
							<option value="Congo, The Democratic Republic of The">Congo, The Democratic Republic of The</option> 
							<option value="Cook Islands">Cook Islands</option> 
							<option value="Costa Rica">Costa Rica</option> 
							<option value="Cote D'ivoire">Cote D'ivoire</option> 
							<option value="Croatia">Croatia</option> 
							<option value="Cuba">Cuba</option> 
							<option value="Cyprus">Cyprus</option> 
							<option value="Czech Republic">Czech Republic</option> 
							<option value="Denmark">Denmark</option> 
							<option value="Djibouti">Djibouti</option> 
							<option value="Dominica">Dominica</option> 
							<option value="Dominican Republic">Dominican Republic</option> 
							<option value="Ecuador">Ecuador</option> 
							<option value="Egypt">Egypt</option> 
							<option value="El Salvador">El Salvador</option> 
							<option value="Equatorial Guinea">Equatorial Guinea</option> 
							<option value="Eritrea">Eritrea</option> 
							<option value="Estonia">Estonia</option> 
							<option value="Ethiopia">Ethiopia</option> 
							<option value="Falkland Islands (Malvinas)">Falkland Islands (Malvinas)</option> 
							<option value="Faroe Islands">Faroe Islands</option> 
							<option value="Fiji">Fiji</option> 
							<option value="Finland">Finland</option> 
							<option value="France">France</option> 
							<option value="French Guiana">French Guiana</option> 
							<option value="French Polynesia">French Polynesia</option> 
							<option value="French Southern Territories">French Southern Territories</option> 
							<option value="Gabon">Gabon</option> 
							<option value="Gambia">Gambia</option> 
							<option value="Georgia">Georgia</option> 
							<option value="Germany">Germany</option> 
							<option value="Ghana">Ghana</option> 
							<option value="Gibraltar">Gibraltar</option> 
							<option value="Greece">Greece</option> 
							<option value="Greenland">Greenland</option> 
							<option value="Grenada">Grenada</option> 
							<option value="Guadeloupe">Guadeloupe</option> 
							<option value="Guam">Guam</option> 
							<option value="Guatemala">Guatemala</option> 
							<option value="Guinea">Guinea</option> 
							<option value="Guinea-bissau">Guinea-bissau</option> 
							<option value="Guyana">Guyana</option> 
							<option value="Haiti">Haiti</option> 
							<option value="Heard Island and Mcdonald Islands">Heard Island and Mcdonald Islands</option> 
							<option value="Holy See (Vatican City State)">Holy See (Vatican City State)</option> 
							<option value="Honduras">Honduras</option> 
							<option value="Hong Kong">Hong Kong</option> 
							<option value="Hungary">Hungary</option> 
							<option value="Iceland">Iceland</option> 
							<option value="India">India</option> 
							<option value="Indonesia">Indonesia</option> 
							<option value="Iran, Islamic Republic of">Iran, Islamic Republic of</option> 
							<option value="Iraq">Iraq</option> 
							<option value="Ireland">Ireland</option> 
							<option value="Israel">Israel</option> 
							<option value="Italy">Italy</option> 
							<option value="Jamaica">Jamaica</option> 
							<option value="Japan">Japan</option> 
							<option value="Jordan">Jordan</option> 
							<option value="Kazakhstan">Kazakhstan</option> 
							<option value="Kenya">Kenya</option> 
							<option value="Kiribati">Kiribati</option> 
							<option value="Korea, Democratic People's Republic of">Korea, Democratic People's Republic of</option> 
							<option value="Korea, Republic of">Korea, Republic of</option> 
							<option value="Kuwait">Kuwait</option> 
							<option value="Kyrgyzstan">Kyrgyzstan</option> 
							<option value="Lao People's Democratic Republic">Lao People's Democratic Republic</option> 
							<option value="Latvia">Latvia</option> 
							<option value="Lebanon">Lebanon</option> 
							<option value="Lesotho">Lesotho</option> 
							<option value="Liberia">Liberia</option> 
							<option value="Libyan Arab Jamahiriya">Libyan Arab Jamahiriya</option> 
							<option value="Liechtenstein">Liechtenstein</option> 
							<option value="Lithuania">Lithuania</option> 
							<option value="Luxembourg">Luxembourg</option> 
							<option value="Macao">Macao</option> 
							<option value="Macedonia, The Former Yugoslav Republic of">Macedonia, The Former Yugoslav Republic of</option> 
							<option value="Madagascar">Madagascar</option> 
							<option value="Malawi">Malawi</option> 
							<option value="Malaysia">Malaysia</option> 
							<option value="Maldives">Maldives</option> 
							<option value="Mali">Mali</option> 
							<option value="Malta">Malta</option> 
							<option value="Marshall Islands">Marshall Islands</option> 
							<option value="Martinique">Martinique</option> 
							<option value="Mauritania">Mauritania</option> 
							<option value="Mauritius">Mauritius</option> 
							<option value="Mayotte">Mayotte</option> 
							<option value="Mexico">Mexico</option> 
							<option value="Micronesia, Federated States of">Micronesia, Federated States of</option> 
							<option value="Moldova, Republic of">Moldova, Republic of</option> 
							<option value="Monaco">Monaco</option> 
							<option value="Mongolia">Mongolia</option> 
							<option value="Montserrat">Montserrat</option> 
							<option value="Morocco">Morocco</option> 
							<option value="Mozambique">Mozambique</option> 
							<option value="Myanmar">Myanmar</option> 
							<option value="Namibia">Namibia</option> 
							<option value="Nauru">Nauru</option> 
							<option value="Nepal">Nepal</option> 
							<option value="Netherlands">Netherlands</option> 
							<option value="Netherlands Antilles">Netherlands Antilles</option> 
							<option value="New Caledonia">New Caledonia</option> 
							<option value="New Zealand">New Zealand</option> 
							<option value="Nicaragua">Nicaragua</option> 
							<option value="Niger">Niger</option> 
							<option value="Nigeria">Nigeria</option> 
							<option value="Niue">Niue</option> 
							<option value="Norfolk Island">Norfolk Island</option> 
							<option value="Northern Mariana Islands">Northern Mariana Islands</option> 
							<option value="Norway">Norway</option> 
							<option value="Oman">Oman</option> 
							<option value="Pakistan">Pakistan</option> 
							<option value="Palau">Palau</option> 
							<option value="Palestinian Territory, Occupied">Palestinian Territory, Occupied</option> 
							<option value="Panama">Panama</option> 
							<option value="Papua New Guinea">Papua New Guinea</option> 
							<option value="Paraguay">Paraguay</option> 
							<option value="Peru">Peru</option> 
							<option value="Philippines">Philippines</option> 
							<option value="Pitcairn">Pitcairn</option> 
							<option value="Poland">Poland</option> 
							<option value="Portugal">Portugal</option> 
							<option value="Puerto Rico">Puerto Rico</option> 
							<option value="Qatar">Qatar</option> 
							<option value="Reunion">Reunion</option> 
							<option value="Romania">Romania</option> 
							<option value="Russian Federation">Russian Federation</option> 
							<option value="Rwanda">Rwanda</option> 
							<option value="Saint Helena">Saint Helena</option> 
							<option value="Saint Kitts and Nevis">Saint Kitts and Nevis</option> 
							<option value="Saint Lucia">Saint Lucia</option> 
							<option value="Saint Pierre and Miquelon">Saint Pierre and Miquelon</option> 
							<option value="Saint Vincent and The Grenadines">Saint Vincent and The Grenadines</option> 
							<option value="Samoa">Samoa</option> 
							<option value="San Marino">San Marino</option> 
							<option value="Sao Tome and Principe">Sao Tome and Principe</option> 
							<option value="Saudi Arabia">Saudi Arabia</option> 
							<option value="Senegal">Senegal</option> 
							<option value="Serbia and Montenegro">Serbia and Montenegro</option> 
							<option value="Seychelles">Seychelles</option> 
							<option value="Sierra Leone">Sierra Leone</option> 
							<option value="Singapore">Singapore</option> 
							<option value="Slovakia">Slovakia</option> 
							<option value="Slovenia">Slovenia</option> 
							<option value="Solomon Islands">Solomon Islands</option> 
							<option value="Somalia">Somalia</option> 
							<option value="South Africa">South Africa</option> 
							<option value="South Georgia and The South Sandwich Islands">South Georgia and The South Sandwich Islands</option> 
							<option value="Spain">Spain</option> 
							<option value="Sri Lanka">Sri Lanka</option> 
							<option value="Sudan">Sudan</option> 
							<option value="Suriname">Suriname</option> 
							<option value="Svalbard and Jan Mayen">Svalbard and Jan Mayen</option> 
							<option value="Swaziland">Swaziland</option> 
							<option value="Sweden">Sweden</option> 
							<option value="Switzerland">Switzerland</option> 
							<option value="Syrian Arab Republic">Syrian Arab Republic</option> 
							<option value="Taiwan, Province of China">Taiwan, Province of China</option> 
							<option value="Tajikistan">Tajikistan</option> 
							<option value="Tanzania, United Republic of">Tanzania, United Republic of</option> 
							<option value="Thailand">Thailand</option> 
							<option value="Timor-leste">Timor-leste</option> 
							<option value="Togo">Togo</option> 
							<option value="Tokelau">Tokelau</option> 
							<option value="Tonga">Tonga</option> 
							<option value="Trinidad and Tobago">Trinidad and Tobago</option> 
							<option value="Tunisia">Tunisia</option> 
							<option value="Turkey">Turkey</option> 
							<option value="Turkmenistan">Turkmenistan</option> 
							<option value="Turks and Caicos Islands">Turks and Caicos Islands</option> 
							<option value="Tuvalu">Tuvalu</option> 
							<option value="Uganda">Uganda</option> 
							<option value="Ukraine">Ukraine</option> 
							<option value="United Arab Emirates">United Arab Emirates</option> 
							<option value="United Kingdom">United Kingdom</option> 
							<option value="United States">United States</option> 
							<option value="United States Minor Outlying Islands">United States Minor Outlying Islands</option> 
							<option value="Uruguay">Uruguay</option> 
							<option value="Uzbekistan">Uzbekistan</option> 
							<option value="Vanuatu">Vanuatu</option> 
							<option value="Venezuela">Venezuela</option> 
							<option value="Viet Nam">Viet Nam</option> 
							<option value="Virgin Islands, British">Virgin Islands, British</option> 
							<option value="Virgin Islands, U.S.">Virgin Islands, U.S.</option> 
							<option value="Wallis and Futuna">Wallis and Futuna</option> 
							<option value="Western Sahara">Western Sahara</option> 
							<option value="Yemen">Yemen</option> 
							<option value="Zambia">Zambia</option> 
							<option value="Zimbabwe">Zimbabwe</option>
						</select>
					</span>
				</li>
"""
ss_form_howhear = """						
				<li>
					<span class="contact-label">
						<label for="ss-form-howhear">
							How did you hear about us? *
						</label>
					</span>
					<span class="contact-select">
						<select name="ss-form-howhear" id="ss-form-howhear">
							<option value="">
								Please select...
							</option>
							<option value="Food Product Design Magazine">
								Food Product Design Magazine
							</option>
							<option value="Food Product Design Website">
								Food Product Design Website
							</option>
							<option value="Prepared Foods Magazine">
								Prepared Foods Magazine
							</option> 
							<option value="Prepared Foods Website">
								Prepared Foods Website
							</option> 
							<option value="Food Master">
								Food Master
							</option> 
							<option value="Culinology">
								Culinology
							</option> 
							<option value="Roast">
								Roast
							</option> 
							<option value="Annual Buyers Guide">
								Annual Buyers Guide
							</option> 
							<option value="Search Engine">
								Search Engine
							</option> 
							<option value="Word of Mouth">
								Word of Mouth
							</option> 
							<option value="Trade Show">
								Trade Show
							</option> 
							<option value="Beverage Industry">
								Beverage Industry
							</option> 
							<option value="Email Promotion">
								Email Promotion
							</option> 
							<option value="Existing Customer">
								Existing Customer
							</option>
							<option value="Other">
								Other
							</option>
						</select>
					</span>
				</li>
"""
ss_form_howhelp = """		
				<li>
					<span class="contact-label">
						<label for="ss-form-howhelp">
							How can we help you? *
						</label>
					</span>
					<span class="contact-textarea">
						<textarea rows="8" name="ss-form-howhelp" id="ss-form-howhelp"></textarea>
					</span>
				</li>
"""

ss_form_inputs = {
	'ss-form-name': ss_form_name,
	'ss-form-title': ss_form_title,
	'ss-form-email': ss_form_email,
	'ss-form-phone': ss_form_phone,
	'ss-form-company': ss_form_company,
	'ss-form-address': ss_form_address,
	'ss-form-city': ss_form_city,
	'ss-form-state': ss_form_state,
	'ss-form-zip': ss_form_zip,
	'ss-form-country': ss_form_country,
	'ss-form-howhear': ss_form_howhear,
	'ss-form-howhelp': ss_form_howhelp,
}

ss_form_order = (
	'ss-form-name',
	'ss-form-title',
	'ss-form-email',
	'ss-form-phone',
	'ss-form-company',
	'ss-form-address',
	'ss-form-city',
	'ss-form-state',
	'ss-form-zip',
	'ss-form-country',
	'ss-form-howhear',
	'ss-form-howhelp',
)

def ty_redirect(form_data):
	import smtplib
	user = 'contactus@flavordynamics.com'
	pw = 'zi+jl_r7'
	serveraddr = 'smtp.gmail.com'
	toaddrs = ['steves@flavordynamics.com','fdileague@gmail.com','colleenr@flavordynamics.com','contactus@flavordynamics.com']
	subject = 'contact us'
	
	from email.MIMEMultipart import MIMEMultipart
	msg = MIMEMultipart()
	msg['Subject'] = subject
	msg['From'] = user
	msg['To'] = ", ".join(toaddrs)
	
	sorted_form_data = []
	csv_headers = []
	for k in ss_form_order:
		csv_headers.append(k)
		try:
			sorted_form_data.append(form_data[k])
		except:
			sorted_form_data.append('')
	csv_headers_str = ','.join(csv_headers)
	csv_headers_str+='\r\n'
	csv_line = ','.join(sorted_form_data)
	csv_line+='\r\n'
	
	import cStringIO
	output = cStringIO.StringIO()
	output.write(csv_headers_str)
	output.write(csv_line)
	
	from email.MIMEText import MIMEText
	csv_attach = MIMEText(output.getvalue())
	msg_body = output.getvalue()
	
	msg.attach(csv_attach)
	
	ms = smtplib.SMTP(serveraddr,587)
	ms.ehlo()
	ms.starttls()
	ms.ehlo()
	ms.login(user,pw)
	ms.sendmail(user,toaddrs,msg.as_string())
	ms.quit()
	
	print "Location: http://www.flavordynamics.com/thankyou.html"
	return

def validate_email(email):
	if email is None:
		return False
	if len(email) < 7:
		return False
	if re.search("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) == None:
		return False
	return True

def validate_phone(phone, country):
	if country == "United States":
		if re.search(r'''
		                # don't match beginning of string, number can start anywhere
		    (\d{3})     # area code is 3 digits (e.g. '800')
		    \D*         # optional separator is any number of non-digits
		    (\d{3})     # trunk is 3 digits (e.g. '555')
		    \D*         # optional separator
		    (\d{4})     # rest of number is 4 digits (e.g. '1212')
		    \D*         # optional separator
		    (\d*)       # extension is optional and can be any number of digits
		    $           # end of string
		    ''',phone):
			return True
		elif (len(phone) > 7 and 
			re.search(r'\d+', phone)):
			return True
		else:
			return False
	else:
		try:
			if len(phone) > 5:
				return True
			else:
				return False
		except:
			return False

form = cgi.FieldStorage()
if form.has_key('ss-form-name'):
	form_data = {}
	form_data['ss-form-name'] = form.getfirst('ss-form-name', None)
	form_data['ss-form-title'] = form.getfirst('ss-form-title', None)
	form_data['ss-form-email'] = form.getfirst('ss-form-email', None)
	form_data['ss-form-phone'] = form.getfirst('ss-form-phone', None)
	form_data['ss-form-company'] = form.getfirst('ss-form-company', None)
	form_data['ss-form-address'] = form.getfirst('ss-form-address', None)
	form_data['ss-form-city'] = form.getfirst('ss-form-city', None)
	form_data['ss-form-state'] = form.getfirst('ss-form-state', None)
	form_data['ss-form-zip'] = form.getfirst('ss-form-zip', None)
	form_data['ss-form-country'] = form.getfirst('ss-form-country', None)
	form_data['ss-form-howhear'] = form.getfirst('ss-form-howhear', None)
	form_data['ss-form-howhelp'] = form.getfirst('ss-form-howhelp', None)
	
	validation_messages = {}
	if form_data['ss-form-name'] is None:
		validation_messages['ss-form-name'] = 'Please fill in your name.'	
	else:
		ss_form_inputs['ss-form-name'] = ss_form_inputs['ss-form-name'].replace('value=""',
																				'value="%s"' % form_data['ss-form-name'])

	if not validate_email(form_data['ss-form-email']): 
		validation_messages['ss-form-email'] = 'Please fill in your e-mail address.'
	else:
		ss_form_inputs['ss-form-email'] = ss_form_inputs['ss-form-email'].replace('value=""',
																				'value="%s"' % form_data['ss-form-email'])

	if form_data['ss-form-country'] is None:
		validation_messages['ss-form-country'] = 'Please fill in your country.'
	else:
				ss_form_inputs['ss-form-country'] = ss_form_inputs['ss-form-country'].replace(
																					'value="%s"' % form_data['ss-form-country'],
																					'value="%s" SELECTED' % form_data['ss-form-country'])
					
	if not validate_phone(form_data['ss-form-phone'], form_data['ss-form-country']):
		validation_messages['ss-form-phone'] = 'Please fill in your phone number.'	
	else:
		ss_form_inputs['ss-form-phone'] = ss_form_inputs['ss-form-phone'].replace('value=""',
																				'value="%s"' % form_data['ss-form-phone'])
		
	if form_data['ss-form-company'] is None:
		validation_messages['ss-form-company'] = 'Please fill in your company name.'
	else:
		ss_form_inputs['ss-form-company'] = ss_form_inputs['ss-form-company'].replace('value=""',
																				'value="%s"' % form_data['ss-form-company'])
				
	if form_data['ss-form-address'] is None:
		validation_messages['ss-form-address'] = 'Please fill in your address.'	
	else:
		ss_form_inputs['ss-form-address'] = ss_form_inputs['ss-form-address'].replace('value=""',
																				'value="%s"' % form_data['ss-form-address'])
		
	if form_data['ss-form-city'] is None:
		validation_messages['ss-form-city'] = 'Please fill in your city.'	
	else:
		ss_form_inputs['ss-form-city'] = ss_form_inputs['ss-form-city'].replace('value=""',
																				'value="%s"' % form_data['ss-form-city'])
			
	if form_data['ss-form-state'] is None:
		validation_messages['ss-form-state'] = 'Please fill in your state.'	
	else:
		ss_form_inputs['ss-form-state'] = ss_form_inputs['ss-form-state'].replace('value=""',
																				'value="%s"' % form_data['ss-form-state'])
			
	if (form_data['ss-form-zip'] is None or
		not re.search("\d{5}(?:[-\s]\d{4})?", form_data['ss-form-zip'])):
		validation_messages['ss-form-zip'] = 'Please fill in your zip code.'
	else:
		ss_form_inputs['ss-form-zip'] = ss_form_inputs['ss-form-zip'].replace('value=""',
																				'value="%s"' % form_data['ss-form-zip'])
				
	if form_data['ss-form-howhear'] is None:
		validation_messages['ss-form-howhear'] = 'Please tell us how you heard about us.'	
	else:
		ss_form_inputs['ss-form-howhear'] = ss_form_inputs['ss-form-howhear'].replace(
																					'value="%s"' % form_data['ss-form-howhear'],
																					'value="%s" SELECTED' % form_data['ss-form-howhear'])
			
	if form_data['ss-form-howhelp'] is None:
		validation_messages['ss-form-howhelp'] = 'Please tell us how we can help you.'
	else:
				ss_form_inputs['ss-form-howhelp'] = ss_form_inputs['ss-form-howhelp'].replace('></textarea>',
																				'>%s</textarea>' % form_data['ss-form-howhelp'])
				
	if len(validation_messages) == 0:
		ty_redirect(form_data)
			

print "Content-type: text/html"
print """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html><head>

<meta http-equiv="MSThemeCompatible" Content="No"/>
<meta name="MSSmartTagsPreventParsing" content="true"/>
<meta http-equiv="imagetoolbar" content="no"/>
<meta http-equiv="X-UA-Compatible" content="IE=8"/>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<link rel="alternate" title="Top Flavors of the Day" href="http://www.flavordynamics.com/rss.xml" type="application/rss+xml">
<link href="http://www.flavordynamics.com/css/fdi.css?v=9" rel="stylesheet" type="text/css">
<link rel="stylesheet" type="text/css" href="http://www.flavordynamics.com/jqueryslidemenu.css?v=9" />

<!-- Testing
<link href="contact.css?v=9" rel="stylesheet" type="text/css">
-->
<!-- production row-->
<link href="http://www.flavordynamics.com/css/contact.css?v=9" rel="stylesheet" type="text/css">


<!--[if lte IE 7]>
<style type="text/css">
html .jqueryslidemenu{height: 1%;} /*Holly Hack for IE7 and below*/
</style>
<![endif]-->

<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.2.6/jquery.min.js"></script>

<script type="text/javascript" src="http://www.flavordynamics.com/jqueryslidemenu.js"></script>


<title>Welcome to Flavor Dynamics, Inc.</title>

</head>

<body>
	
<div id="container">
	
<div id="header"><img src="http://www.flavordynamics.com/images/Untitled-1_01.png" width="167" height="103"><img src="http://www.flavordynamics.com/images/Untitled-1_02.png" width="302" height="103"><img src="http://www.flavordynamics.com/images/Untitled-1_03.png" width="428" height="103"></div><!-- Closes the Header div -->

<div id="menubar">
	
<div id="myslidemenu" class="jqueryslidemenu">
  <ul>
    <li><a href="http://www.flavordynamics.com/index.html">Home</a></li>
    <li><a href="http://www.flavordynamics.com/spotlight.html">Products & Services</a>
      <ul>
        <li><a href="http://www.flavordynamics.com/spotlight.html">Product Spotlight</a></li>
        <li><a href="http://www.flavordynamics.com/sweet.html">Sweet Flavors</a></li>
        <li><a href="http://www.flavordynamics.com/savory.html">Savory Flavors</a></li>
        <li><a href="http://www.flavordynamics.com/beverage.html">Beverage Flavors</a></li>
        <li><a href="http://www.flavordynamics.com/coffee.html">Coffee Flavors</a></li>
        <li><a href="http://www.flavordynamics.com/tea.html">Tea Flavors</a></li>
        <li><a href="http://www.flavordynamics.com/downloads.html">Product Sheet Downloads</a></li>
      </ul>
    </li>
    <li><a href="http://www.flavordynamics.com/wwd.html">About FDI</a>
      <ul>
        <li><a href="http://www.flavordynamics.com/wwd.html">What We Do</a></li>
        <li><a href="http://www.flavordynamics.com/history.html">History</a></li>
        <li><a href="http://www.flavordynamics.com/classes.html">Classes</a></li>            
        <li><a href="http://www.flavordynamics.com/calendar.html">Calendar</a></li>
      </ul>
    </li>
    <li><a href="http://www.flavordynamics.com/tech.html">Innovation</a>
      <ul>
        <li><a href="http://www.flavordynamics.com/tech.html#">Technology</a></li>
        <li><a href="http://www.flavordynamics.com/product.html">Innovative Product Lines</a></li>
        <li><a href="http://www.flavordynamics.com/edu.html">Educational Tools</a></li>
      </ul>
    </li>
    <li><a href="http://www.flavordynamics.com/contact.html">Contact</a></li>
  </ul>
  <br style="clear: left" />
</div>
<!--Close Menu Controls div -->
</div>
<!--Close Menubar div -->
 <div id="wrap">
	    
	<div class="ss-form-container">
		<div class="ss-form-heading ss-form-title">
			Contact Us
			<hr class="ss-email-break" style="display:none;">
			<div class="ss-required-asterisk">
				* Required&nbsp;&nbsp;
				<ul class="ss-required-asterisk">
"""

for k in ss_form_order:
	try:
		print "<li>%s</li>" % validation_messages[k]
		ss_form_inputs[k] = ss_form_inputs[k].replace(r'class="contact-label"',
													r'class="validate-me" class="contact-label"')
	except:
		pass
	
print """
				</ul>
			</div>
		</div> 
	
		<div class="ss-form">
		<form action="http://www.flavordynamics.com/cgi-bin/test.py" method="post" id="ss-form">
			<ul id="ss-form-control-list">
"""

for k in ss_form_order:
	print ss_form_inputs[k]

print """
			</ul>
			<input type="submit" name="submit" value="Submit">
		</form>
		</div>
	</div>
	<div id="prodser">
		Flavor Dynamics, Inc. handles a wide variety of flavoring applications, from large-scale production flavors to smaller-scale custom orders. We have a low minimum order and are eager to help small businesses grow, yet we are very capable of producing large-scale industrial orders in our on-site production facilities.
	    <p>
	    	Please contact our Customer Care Department with any sample requests.
		</p>
		<p>	
			<strong>FDI Phone:</strong> 888-271-8424<br>
	       	<strong>FDI Fax:</strong> 908-822-8547<br>
			<strong>FDI E-mail:</strong> customercare@flavordynamics.com
		</p>
	    <p>
	    	<strong>FDI Mailing Address:</strong><br>
	        Flavor Dynamics, Inc.<br>
	        640 Montrose Ave<br>
			South Plainfield, NJ&nbsp; 07080
		</p>                  
		<p></p>                  
		<p>
			We are sorry for the inconvenience, but if you submitted contact info in the month of January we did not receive it.  If you resubmit we will get back to you immediately.
		</p>
	</div>	
	
</div><!-- Closes the wrap div -->
<div id="footer">
<hr>
® 2010 Flavor Dynamics, Inc. | <a href="http://www.flavordynamics.com/index.html">Home</a> | <a href="http://www.flavordynamics.com/spotlight.html">Product Spotlight</a> | <a href="http://www.flavordynamics.com/sweet.html">Sweet Flavors</a> | <a href="http://www.flavordynamics.com/savory.html">Savory Flavors</a> | <a href="http://www.flavordynamics.com/beverage.html">Beverage Flavors</a> | <a href="http://www.flavordynamics.com/coffee">Coffee Flavors</a><br>
<a href="http://www.flavordynamics.com/tea">Tea Flavors</a> | <a href="http://www.flavordynamics.com/wwd.html">What We Do</a> | <a href="http://www.flavordynamics.com/history">History</a> | <a href="http://www.flavordynamics.com/classes">Classes</a> | <a href="http://www.flavordynamics.com/downloads.html">Downloads</a> | <a href="http://www.flavordynamics.com/calander">Calendar</a> | <a href="http://www.flavordynamics.com/tech.html">Technology</a> | <a href="http://www.flavordynamics.com/product">Innovative Product Lines</a> | <a href="http://www.flavordynamics.com/edu.html">Educational Tools</a> | <a href="http://www.flavordynamics.com/contact.html">Contact</a>
</div> 
  
</div><!-- Closes the container div -->

</body></html>
"""