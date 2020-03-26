#!/usr/bin/env python
# -*- coding: utf-8 -*-

# gbpp

# wiki = [
#     (
#         'Any sign of tampering of product or equipment you should alert',
#     ),
#     (
#         'If you see any suspicious criminal activity, alert the manager who will alert',
#     ),
#     (
#         'Outside contractors in unauthorized areas or if you receive unexpected mail or packages alert',
#     ),
#     (
#         'Truckers are the only people other than employees and routine outside contractors (Once signed in) that can enter the side doors',
#     ),
#     (
#         'Truckers can use the men’s locker room lavatories?',
#     ),
#     (
#         'Any government inspector can review a record as long as they show a badge',
#     ),
#     (
#         'Any non-personal visitor coming into the building must sign a secrecy agreement for the first time.',
#     ),
#
# ]

# colorblind
#
# hazcom
#
# fooddefense
#
# ccp
#
# fltv
#
# wpsafety



bacteria = [
    (   'Bacteria are:',
        [
            'Living organisms so small they can only be seen with the help of a microscope',
            'Living organisms large enough to be seen with the naked eye',
            'Organisms that are made of "micros"',
            'None of the above'
        ],
        '1'
    ),
    (
        'Bacteria are found in:',
        [
            'Food',
            'Soil',
            'Intestines of people and animals',
            'All of the above'
        ],
        '2'
    ),
    (
        'Bacteria are used to make:',
        [
            'Bread',
            'Cheese',
            'Summer sausage',
            'All of the above'
        ],
        '3'
    ),
    (
        'Which is not a harmful bacteria:',
        [
            'Listeria',
            'E. coli',
            'Zoology',
            'Salmonella'
        ],
        '4'
    ),
    (
        'Disease caused by harmful bacteria is called:',
        [
            'Microbial poisioning',
            'Foodborne illness',
            'Food contamination',
            'food infection'
        ],
        '5'
    ),
    (
        'A common symptom of ma ny food borne illnesses include:',
        [
            'Vomiting',
            'Blindess',
            'Sleepiness',
            'None of the above'
        ],
        '6'
    ),
    (
        'A procedure food companies use to try to control bacteria is:',
        [
            'Refrigeration',
            'Cleaning and sanitizing',
            'Cooking',
            'All of the above'
        ],
        '7'
    ),
    (
        'The most important personal hygiene practice to control the spread of bacteria is:',
        [
                'Wearing hair restraints',
                'Washing your hands',
                'Bathing daily',
                'None of the above'
        ],
        '8'
    ),
    (
        'Spoilage bacteria can cause food to become:',
        [
            'Mushy',
            'Slimy',
            'Smelly',
            'All of the above'
        ],
        '9'
    ),
    (
        'Ways to prevent the contamination of and control bacteria in food include:',
        [
            'Time and temperature controls',
            'Sanitation',
            'Moisture control',
            'All of the above'
        ],
        '10'
    )
]

foodborne = [
    (
        'Foodborne illness affects how many people each year:',
        [
            '76,000',
            '760,000',
            '76,000,000',
            'None of the above'
        ],
        '1'
    ),
    (
        'Foodborne illness kills how many people each year:',
        [
            '500',
            '5,000',
            '50,000',
            'None of the above'
        ],
        '2'
    ),
    (
        'Foodborne illnesses have been conquered due to improvements in food safety, such as:',
        [
            'Pasteurization of milk',
            'Safe canning',
            'Disinfection of water supplies',
            'All of the above'
        ],
        '3'
    ),
    (
        'New microorganisms emerge as public health problems because:',
        [
            'Microorganisms can evolve',
            'Our environment and the way we live are changing',
            'Food production practices and consumption habits change',
            'All of the above'
        ],
        '4'
    ),
    (
        'When harmful microorganisms are swallowed, they:',
        [
            'Stay in the intestine',
            'Produce a toxin',
            'Invade deep body tissues',
            'All of the above'
        ],
        '5'
    ),
    (
        'Symptoms of food borne illness include:',
        [
            'Diarrhea',
            'Stomach cramps',
            'Nausea',
            'All of the above'
        ],
        '6'
    ),
    (
        'Contaminated food can be very dangerous, especially to:',
        [
            'Pregnant women',
            'Small children',
            'The elderly',
            'All of the above'
        ],
        '7'
    ),
    (
        'Treatment of foodborne illness typically requires you to:',
        [
            'Eat healthy foods',
            'Get a shot',
            'Drink lots of fluids',
            'None of the above'
        ],
        '8'
    ),
    (
        'Food can become contaminated by:',
        [
            'Infected employees',
            'Cross contamination',
            'Neither a nor b',
            'Both a and b'
        ],
        '9'
    ),
    (
        'Many foodborne illnesses can be prevented by:',
        [
            'Practicing good personal hygiene',
            'Properly cleaning and sanitizing equipment and work areas',
            'Following time and temperature controls',
            'All of the above'
        ],
        '10'
    )
]

personalhygiene = [
    (
        'Personal hygiene is:',
        [
            'Keeping yourself clean',
            'Sanitizing of equipment and food work areas',
            'Coming to work on time',
            'None ofthe above'
        ],
        '1'
    ),
    (
        'Which is not a good personal hygiene practice:',
        [
            'Bathing daily',
            'Wearing hair restraints',
            'Wearing clean jewelry',
            'Handwashing',
        ],
        '2'
    ),
    (
        'Good personal hygiene practices include:',
        [
            'Not working when s ick or infectious',
            'Wearing clean clothes to work',
            'Trimming, cleaning, and filing fingernails frequently',
            'All of the above',
        ],
        '3'
    ),
    (
        'Which item can be brough t into food work a reas :',
        [
            'Chewing gum',
            'Hair restraints',
            'Lunches',
            'Candy',
        ],
        '4'
    ),
    (
        'Personal protective equipment (PPE) in cludes:',
        [
            'Gloves',
            'Plastic sleeves',
            'Smocks',
            'All of the above',
        ],
        '5'
    ),
    (
        'When wearing person al protective equipment (PPE), you should:',
        [
            'Modify the cut or style',
            'Keep it clean a nd uncontamina ted, and change it when it becomes torn or soiled',
            'Keep it on until the end of your shift, even if it is contaminated',
            'None of the above',
        ],
        '6'
    ),
    (
        'How many steps are involved in a proper hand washing procedure:',
        [
            'Seven',
            'Five',
            'One',
            'Two',
        ],
        '7'
    ),
    (
        'You must always wash your hands after:',
        [
            'Using the restroom for any reason',
            'Touching or scratching any part of your skin, hair, eyes, or mouth',
            'Eating, drinking, or smoking',
            'All of the above',
        ],
        '8'
    ),
    (
        'Proper handwashing technique should include which of the following:',
        [
            'Do not worry about cleaning under your fingernails or between fingers',
            'Using the coldest water possible',
            'Using the germicidal/anti-bacterial soap or sanitizer provided',
            'Drying your hands on your uniform',
        ],
        '9'
    ),
    (
        'Where can lunches, drinks, candy, and chewing gum be allowed in food facilities:',
        [
            'In processing areas',
            'Only in lunchrooms, break areas, or other designated storage areas',
            'In clothing storage or changing room areas',
            'All of the above',
        ],
        '10'
    )
]

haccp = [
    (
        'HACCP stands for:',
        [
            'Hazard Analysis and Critical Control Points',
            'Hazards and Allergens Cause Certain Problems',
            'Having any Affects Causes Control Policies',
            'None of the above',
        ],
        '1'
    ),
    (
        'The purpose of HACCP is to:',
        [
            'Make you do more work',
            'Eliminate potential hazards from food to make it safe to eat',
            'Clean equipmen t properly',
            'None of the above',
        ],
        '2'
    ),
    (
        'HACCP identifies which types ofhazards:',
        [
            'Biological',
            'Chemical',
            'Physical',
            'All of the above',
        ],
        '3'
    ),
    (
        'Which U.S. government agencies require HACCP:',
        [
            'United States Department of Agriculture',
            'Food and Drug Administration',
            'Both (a ) and (b)',
            'Neither (a ) nor (b',
        ],
        '4'
    ),
    (
        'How many HACCP principles are there:',
        [
            'Five',
            'Three',
            'Seven',
            'Eight',
        ],
        '5'
    ),
    (
        'Which is not a principle of HACCP:',
        [
            'Hazard analysis',
            'HACCP team',
            'Monitoring',
            'Recordkeeping',
        ],
        '6'
    ),
    (
        'Which is an example of a physical hazard:',
        [
            'Glass',
            'Cleaning chemicals',
            'Bacteria',
            'None of the above',
        ],
        '7'
    ),
    (
        'Which type of hazard is the cause of food borne illness:',
        [
            'Physical',
            'Biological',
            'Chemical',
            'None of the above',
        ],
        '8'
    ),
    (
        'A critical control point (CCP) is:',
        [
            'Identifying hazards and preventive measures',
            'A point, step, or procedure in a food process at which a hazard can be controlled',
            'Product sampling and testing',
            'All of the above',
        ],
        '9'
    ),
    (
        'HACCP records must be:',
        [
            'Accurate',
            'Signed',
            'Dated',
            'All of the above',
        ],
        '10'
    )
]

sanitation = [
    (
        'Sanitation refers to:',
        [
            'Only cleaning of equipment and food work areas',
            'Only sanitizing of equipment and food work areas',
            'All of the practices and procedures used to keep the facility clean and the food produced uncontaminated',
            'Cleaning and sanitizing of non-food work areas',
        ],
        '1'
    ),
    (
        'Which of the topics are related to sanitation:',
        [
            'Personal hygiene and cleanliness',
            'Equipment and work area clothing',
            'Pest control',
            'All of the above',
        ],
        '2'
    ),
    (
        'Which does not require strict sanitation procedures be followed:',
        [
            "Food production equipment",
            "Employees' automobiles",
            "Food production work areas",
            "Employees' personal hygiene",
        ],
        '3'
    ),
    (
        'Food residue left on equipment is:',
        [
            'A source of food for bacteria',
            'A source of chemical contamination',
            'Ok, it does not need to be cleaned off',
            'All of the above',
        ],
        '4'
    ),
    (
        'How many steps are in a basic cleaning and sanitizing procedure:',
        [
            'One',
            'Two',
            'Three',
            'Four',
        ],
        '5'
    ),
    (
        'The basic steps of cleaning and sanitizing include:',
        [
            'A rough clean',
            'Cleaning with a chemical',
            'Sanitizing',
            'All of the above',
        ],
        '6'
    ),
    (
        'Methods of applying cleaning and sanitizing chemicals include:',
        [
            'Mixing with water and apply with a brush',
            'Metering and apply through a hose',
            'Applying as a foam',
            'All of the above',
        ],
        '7'
    ),
    (
        'Cleaning and sanitizing equipment and chemicals should be:',
        [
            'Left any old place in the plant after use',
            'Used, handled, and stored properly',
            'Put away when still wet',
            'None of the above',
        ],
        '8'
    ),
    (
        'When storing cleaning and sanitizing equipment, make sure to:',
        [
            'Clean the equipment after each use',
            'Dry the equipment thoroughly before putting it away',
            'Store the equipment only in its designated storage area',
            'All of the above',
        ],
        '9'
    ),
    (
        'When using cleaning and sanitizing chemicals always:',
        [
            'Read and following the label instructions carefully',
            'Do whatever way you want',
            'Use as much or as little as you want',
            'None of the above',
        ],
        '10'
    )
]

time =[
    (
        'The temperature "Danger Zone" is between:',
        [
            '20 and 120 degrees F',
            '30 and 130 degrees F',
            '40 and 140 degrees F',
            '50 and 150 degrees F',
        ],
        '1'
    ),
    (
        'Time and temperature controls are used to properly:',
        [
            'Cook food',
            'Cool food',
            'Store food',
            'All of the above',
        ],
        '2'
    ),
    (
        'Time and temperature controls include:',
        [
            'Cooking',
            'Freezing',
            'Pasteurization',
            'All of the above',
        ],
        '3'
    ),
    (
        'The purpose of time and temperature controls is to:',
        [
            'Produce food faster',
            'Control the growth of potentially h a rmful bacteria',
            'Create a warm, moist environment',
            'Make food taste good',
        ],
        '4'
    ),
    (
        'Which bacteria can be controlled by time and temperature:',
        [
            'Listeria',
            'E. coli',
            'Salmonella',
            'All of the above',
        ],
        '5'
    ),
    (
        'Which is the most commonly used time and temperature control in food processing:',
        [
            'Cooking',
            'Irradiation',
            'Thermal processing',
            'All of the above',
        ],
        '6'
    ),
    (
        'Cooling food to about 40 degrees Fahrenheit is called:',
        [
            'Freezing',
            'Pasteurizing',
            'Refrigerating',
            'All of the above',
        ],
        '7'
    ),
    (
        'The first rule to follow for time and temperature controls is:',
        [
            "Being close to target is good enough",
            "Always follow your company's established procedures and practices for the food you are making",
            "If you make a small mistake, it won't matter much",
            "None of the above",
        ],
        '8'
    ),
    (
        'To make sure correct time and temperature controls are met:',
        [
            'Keep doors closed to coolers, freezer, holding areas, warehouses, processing rooms, any other cooled work areas',
            'Never alter the specified time to heat, blanch, cook, or cool a product',
            'Use a thermometer to check if a food has reached its correct processing temperature',
            'All of the above',
        ],
        '9'
    ),
    (
        'If you think a time or temperature control may have been violated:',
        [
            'Tell your supervisor or quality control person, so they can test the batch or make a decision as to what to do',
            'Throw the batch away when no one is looking',
            'Do not tell anyone',
            'None of the above',
        ],
        '10'
    )
]

foreign =[
    (
        'Foreign material detection is:',
        [
            'Finding objects in your morning coffee before going to work',
            'Locating objects in food that should not be there',
            'Sanitizing of equipment and food work areas',
            'None of the above',
        ],
        '1'
    ),
    (
        'Foreign material detection is important because:',
        [
            'It helps ensure that products does not contain foreign objects',
            'It is job security for employees',
            'It helps detect bacteria',
            'None of the above',
        ],
        '2'
    ),
    (
        'Foreign materials can come from :',
        [
            'Raw materials',
            'Inside the plant',
            'Employees',
            'All of the above',
        ],
        '3'
    ),
    (
        'Types of foreign materials include:',
        [
            'Metal',
            'Glass',
            'Wood',
            'All of the above',
        ],
        '4'
    ),
    (
        'Poor personal hygiene practices are the cause of which types of contaminants:',
        [
            'Chewing gum',
            'Hair',
            'Jewelry',
            'All of the above',
        ],
        '5'
    ),
    (
        'It is important to conduct foreign material detection:',
        [
            'When raw materials are received and when food is about to leave the plant',
            'During the cooking process',
            'After the food has arrived at the store',
            'All of the above',
        ],
        '6'
    ),
    (
        'Incoming raw materials can contain which foreign materials:',
        [
            'Pests',
            'Dirt',
            'Debris',
            'All of the above',
        ],
        '7'
    ),
    (
        'Which equipment is used to detect foreign materials:',
        [
            'A thermometer',
            'Magnets and metal detectors',
            'A refrigerator',
            'None of the above',
        ],
        '8'
    ),
    (
        'Visual inspection means:',
        [
            'Looking through a magnifying glass',
            'Using magnets and metal detectors',
            'Looking for foreign materials with the naked eye',
            'None of the above',
        ],
        '9'
    ),
    (
        'Which control measures help prevent foreign materials from getting into food:',
        [
            'Good personal hygiene practices',
            'Inspection of raw materials before adding them to food',
            'Good housekeeping measures',
            'All of the above',
        ],
        '10'
    )
]

cross = [
    (
        'Cross contamination is:',
        [
            'Contamination of food with crosses',
            'Contamination of food with other materials',
            'Contamination of food with ingredients',
            'None of the above',
        ],
        '1'
    ),
    (
        'Which is not a possible contaminant:',
        [
            'Pesticides',
            'Wood',
            'Bacteria',
            'Moon beams',
        ],
        '2'
    ),
    (
        'Chemical contaminants include:',
        [
            'Water',
            'Cleaning chemicals',
            'Milk',
            'All of the above',
        ],
        '3'
    ),
    (
        'To prevent chemical cross contamination always:',
        [
            'Store chemicals in their designated spot when not in use',
            'Make sure food production areas are cleaned, rinsed, and free of chemical residue after sanitation',
            'Put food and packaging materials away or cover them before cleaning or applying pesticides',
            'All of the above',
        ],
        '4'
    ),
    (
        'Bacteria can contamina te food by hitching a ride on:',
        [
            'People',
            'Equipment',
            'Packaging materials',
            'All of the above',
        ],
        '5'
    ),
    (
        'To prevent bacterial cross contamination always:',
        [
            'Was h your hands',
            'Use footbaths and h and dipstations',
            'Separate raw and cooked products',
            'All ofthe a bove',
        ],
        '6'
    ),
    (
        'Physical hazards include:',
        [
            'Metal',
            'Dust',
            'People',
            'Water',
        ],
        '7'
    ),
    (
        'Horseplay includes:',
        [
            'Driving a forklift recklessly',
            'Using hoses to squirt co-workers',
            'Throwing food',
            'All of the above',
        ],
        '8'
    ),
    (
        'Which is not used to detect cross contamination in food:',
        [
            'Metal detector',
            'Screwdriver',
            'Visual inspection',
            'Screens and sifters',
        ],
        '9'
    ),
    (
        'Cross contamination occurs when:',
        [
            'Rules are disobeyed',
            'Control measures are inadequate',
            'There is human error or accident',
            'All of the above',
        ],
        '10'
    )
]

allergens = [
    (
        'A food allergic reaction is ca used by:',
        [
            'Eating too much food',
            "The body's response to a foreign protein",
            'A reaction to harmful bacteria in the food',
            ' All of th e above',
        ],
        '1'
    ),
    (
        'Sufferers of food allergies commonly experience:',
        [
            'Vomiting',
            'Hives',
            'Difficulty breathing',
            'All of the above',
        ],
        '2'
    ),
    (
        'Common food allergen s include:',
        [
            'Peanuts',
            'Milk',
            'Fish',
            'All of the above',
        ],
        '3'
    ),
    (
        'The only way to treat food allergies is to:',
        [
            'Get a shot',
            'Lay down and rest',
            'Avoid foods that trigger reactions',
            'None of the above',
        ],
        '4'
    ),
    (
        'Food a llergens can contaminate products by improper:',
        [
            'Use of ingredients',
            'Use of rework',
            'Clean-up or sanitation of equipment',
            'All ofthe above',
        ],
        '5'
    ),
    (
        'To avoid accidental contamination of ingred ients with allergens:',
        [
            'Check shipments of ingredients and raw materials at receiving',
            'Store a llergenic ingredients separat ely from other ingredients',
            'Always check the ingredients before they are added to a batch of food.',
            'All of th e above',
        ],
        '6'
    ),
    (
        'To avoid allergen contamination when processing products, you should:',
        [
            'Visually inspect equipment for allergen residue or build-up from previous production runs before processing beings on another product',
            'Use separate or color-coded equipment for products that contain a known allergen',
            'Ad the allergen ingredient near the end of processing',
            'All of the above',
        ],
        '7'
    ),
    (
        'Rework that contains an allergen must be:',
        [
            'Clearly labeled',
            'Only used in a compatible product',
            'Both (a) and (b)',
            'Neither (a) nor (b)',
        ],
        '8'
    ),
    (
        'Proper cleanup following the processing of products that contain allergens may include:',
        [
            'Disassembling equipment',
            'Cleaning areas of equipment by hand',
            'Visually inspecting equipment after cleaning',
            'All of the above',
        ],
        '9'
    ),
    (
        'When working with foods that contain allergens, you should always:',
        [
            'Follow all company food safety rules',
            'Work as quickly as possible',
            'Avoid your co-workers',
            'All of the above',
        ],
        '10'
    )
]

pest = [
    (
        'Pests include which of the following:',
        [
            'Insects',
            'Birds',
            'Rodents',
            'All of the above',
        ],
        '1'
    ),
    (
        "Pest control is part of your company's:",
        [
            'Sanitation program',
            'Equipment maintenance',
            'Microbiological testing',
            'None of the above',
        ],
        '2'
    ),
    (
        'Pests are attracted to:',
        [
            'Food',
            'Water',
            'Garbage',
            'All of the above',
        ],
        '3'
    ),
    (
        'The best way to combat pests is to:',
        [
            'Combat them once they arere inside the facility',
            'Keep them from getting into the food facility in the first place',
            'Detect them once they are in the food product',
            'None of the above',
        ],
        '4'
    ),
    (
        'To keep pests from getting in:',
        [
            'The facility s hould be tightly constructed',
            'Eliminate food and water sources',
            'Keep doors a nd windows shut',
            'All of th e above',
        ],
        '5'
    ),
    (
        'Insect control methods include:',
        [
            'Insecticides',
            'Insect electrocutors ("zappers")',
            'Heat sterilization',
            'All of the above',
        ],
        '6'
    ),
    (
        'The methods used to apply pesticides include:',
        [
            'Fogging',
            'Fumigating',
            'Crack-and-crevice spraying',
            'All of the above',
        ],
        '7'
    ),
    (
        'The main method of rodent control is:',
        [
            'Baiting',
            'Trapping',
            'Both (a) and (b)',
            'Neither (a) nor (b)',
        ],
        '8'
    ),
    (
        'A general rule you can follow to help control rodents through baiting include:',
        [
            'Using them only in designated and authorized areas',
            'Inspecting and changing bait frequently',
            'Disposing of, or notifying the proper person to dispose of, any rodent bodies you discover',
            'All of the above',
        ],
        '9'
    ),
    (
        'Which is not an example of good pest control:',
        [
            'Cleaning up spills',
            'Leaving doors and windows open',
            'Cleaning up garbage',
            'Using pesticides',
        ],
        '10'
    )
]

security = [
    (
        'Security risks at your company can include:',
        [
            'Theft',
            'Assault',
            'Vandalism',
            'All of the above',
        ],
        '1'
    ),
    (
        'Parking lots can be dangerous because of:',
        [
            'Unpredictable traffic patterns',
            'Careless drivers',
            'Hidden areas that conceal criminals',
            'All of the above',
        ],
        '2'
    ),
    (
        'When you enter a parking lot you should park:',
        [
            'Where you can clearly see around your vehicle',
            'Where you can be s een',
            'Close to the entrance, if possible',
            'All of the above',
        ],
        '3'
    ),
    (
        'If there is another person in back of you who wants to enter the building, you should:',
        [
            'Let them in if you know them',
            'Insist that they use their own ID badge t o sca n and enter the building',
            'heck their ID badge to see if th ey are the card holder, and then let them in',
            'All of the above',
        ],
        '4'
    ),
    (
        'An area of the plant which must be kept secure is a :',
        [
            'Warehouse',
            'Production area',
            'Laboratory',
            'All of the above',
        ],
        '5'
    ),
    (
        'To protect product while working, you should:',
        [
            'Make sure metal detectors, magnets, etc. are working properly at all times',
            'Properly label product and rework',
            'Report missing stock',
            'All of the above',
        ],
        '6'
    ),
    (
        'To protect yourself while working, you should:',
        [
            'Report suspicious activities',
            'Report broken windows and locks',
            'Be aware of your surroundings at all times',
            'All of the above',
        ],
        '7'
    ),
    (
        'Do not bring lunch containers or purses onto the production floor because:',
        [
            'There is no room for them in your work area',
            'They could be used to conceal chemicals, weapons, and explosive devices',
            'Other employees might take your food',
            'None of the above',
        ],
        '8'
    ),
    (
        'Suspicious activities include:',
        [
            'Acting nervous, anxious, or secretive',
            'Taking pictures of work areas and equipment',
            'Threatening people',
            'All of the above',
        ],
        '9'
    ),
    (
        'Visitors at your company should:',
        [
            'Register before they move about your company',
            'Wear some form of identification',
            'Travel with the employee they have come to see',
            'All of the above',
        ],
        '10'
    )
]

bacteria_sp = [
                (
                    'Las bacterias son:',
                    [
                        'Seres vivientes tan pequeños que solamente se los puede ver con ayuda de un microscopio',
                        'Organismos vivientes lo suficientemente grandes para poderlos ver a simple vista',
                        'Organismos que están hechos de "micros"',
                        'Ninguna de las respuestas de arriba',
                    ],
                    '1'
                ),

                (
                    'Las bacterias se encuentran en:',
                    [
                        'Comida',
                        'Tierra',
                        'Intestinos de personas y animales',
                        'Todos los de arriba',
                    ],
                    '2'
                ),
                (
                    'Se usan bacterias para hacer:',
                    [
                        'Pan',
                        'Queso',
                        'Salchichas de verano',
                        'Todos los de arriba',
                    ],
                    '3'
                ),
                (
                    'Cuál no es una bacteria nociva:',
                    [
                        'Listeria',
                        'E.coli',
                        'Zoología',
                        'Salmonela',
                    ],
                    '4'
                ),
                (
                    'La enfermedad causada por bacteria nociva se llama:',
                    [
                        'Envenenamiento microbiano',
                        'Enfermedades provenientes de la comida',
                        'Contaminación de la comida',
                        'Infección de la comida',
                    ],
                    '5'
                ),
                (
                    'Un síntoma común de muchas de las enfermedades provenientes de la comida incluye:',
                    [
                        'Vómito',
                        'Ceguera',
                        'Ador mecimiento',
                        'Ninguna de las respuestas de arriba',
                    ],
                    '6'
                ),
                (
                    'Un proceso que compañías de alimentos usan para tratar de controlar las bacterias es:',
                    [
                        'Refrigeración',
                        'Limpieza y desinfección',
                        'Cocinar',
                        'Todos los de arriba',
                    ],
                    '7'
                ),
                (
                    'La práctica de higiene personal más importante para controlar la diseminación de bacterias es:',
                    [
                        'Usando redes para el cabello',
                        'Lavándose las manos',
                        'Bañándose diariamente',
                        'Ninguno de los de arriba',
                    ],
                    '8'
                ),
                (
                    'La bacteria proveniente de deterioro puede causar que la comida se haga:',
                    [
                        'Pulposa',
                        'Cienosa',
                        'Apestosa',
                        'Todos los de arriba',
                    ],
                    '9'
                ),
                (
                    'Maneras para prevenir la contaminación y controlar la bacteria en los alimentos incluyen:',
                    [
                        'Controles de tiempo y temperatura',
                        'higiene',
                        'Control de humedad',
                        'Todos los de arriba',
                    ],
                    '10'
                ),
            ]

foodborne_sp = [
                (
                    'Las enfermedades provenientes de los alimentos afectan a cuantas personas cada año:',
                    [
                        '76,000',
                        '760,000',
                        '76,000,000',
                        'Ninguna de las respuestas de arriba',
                    ],
                    '1'
                ),
                (
                    'Las enfermedades provenientes de los alimentos matan a cuantas personas ca da año:',
                    [
                        '500',
                        '5,000',
                        '50,000',
                        'Ninguna de las respuestas de arriba',
                    ],
                    '2'
                ),
                (
                    'Las enfermedades provenientes de los alimentos han sido conquistadas debido a seguridad mejorada de la comida, tal como:',
                    [
                        'La pasteurización de la leche',
                        'Enlatado seguro',
                        'Desinfección de las fuentes de agua',
                        'Todas las de arriba',
                    ],
                    '3'
                ),
                (
                    'Nuevos microorganismos surgen como problemas a la salud pública porque:',
                    [
                        'Los microorganismos pueden evolucionar',
                        'Nuestro entorno y la manera como estamos viviendo está cambiando',
                        'Las prácticas de producción y hábitos de consumo cambian',
                        'Todas las de arriba',
                    ],
                    '4'
                ),
                (
                    'Cuando se traga microorganismos peligrosos, estos :',
                    [
                        'Se quedan en los intestinos',
                        'Producen una toxina',
                        'Invaden tejidos profundos del cuerpo',
                        'Todos los de arriba',
                    ],
                    '5'
                ),
                (
                    'Los síntomas de enfermedades provenientes de los alimentos incluyen:',
                    [
                        'Diarrea',
                        'Retortijones estomacales',
                        'Náusea',
                        'Todas las de arriba',
                    ],
                    '6'
                ),
                (
                    'La comida contaminada puede ser muy peligrosa, especialmente a:',
                    [
                        'Mujeres embarazadas',
                        'Niños pequeños',
                        'Ancianos',
                        'Todas las de arriba',
                    ],
                    '7'
                ),
                (
                    'El tratamiento de enfermedades provenientes de los alimentos tipicamente requiere que uno:',
                    [
                        'Consuma comida saludable',
                        'Reciba una inyección',
                        'Tome muchos líquidos',
                        'Ninguna de las respuestas de arriba',
                    ],
                    '8'
                ),
                (
                    'La comida puede volverse contaminada por:',
                    [
                        'Empleados infectados',
                        'Contaminación entrecruzada',
                        'Ninguna ni a, ni b',
                        'Ambas a, y b',
                    ],
                    '9'
                ),
                (
                    'Se puede prevenir muchas enfermedades provenientes de los alimentos:',
                    [
                        'Practicando buena higiene personal',
                        'Limpiando y desinfectando equipo y áreas de trabajo',
                        'Siguiendo controles de tiempo y temperatura',
                        'Todas las respuestas de arriba',
                    ],
                    '10'
                )

            ]

personalhygiene_sp = [
                (
                    'Higiene personal es:',
                    [
                        'Mantenerse limpio',
                        'Desinfectar el equipo y las áreas de trabajo de alimentos',
                        'Llegar al trabajo a tiempo',
                        'Ninguno de los de arriba',
                    ],
                    '1'
                ),
                (
                    'Cuál no es una buena práctica de higiene personal:',
                    [
                        'Bañarse diariamente',
                        'Usar redes para el cabello',
                        'Usar joyería limpia',
                        'Lavarse las manos',
                    ],
                    '2'
                ),
                (
                    'Las buenas prácticas de higiene personal incluyen:',
                    [
                        'No trabajar cuando esté enfermo o infeccioso',
                        'Usar ropa limpia en el trabajo',
                        'Recortarse, limpiarse, y limarse las uñas frecuentemente',
                        'Todos los de arriba',
                    ],
                    '3'
                ),
                (
                    'Cuál artículo se puede traer a las áreas de trabajo de alimentos:',
                    [
                        'Chicle',
                        'Cubiertas o redes para el cabello',
                        'Almuerzos',
                        'Dulces',
                    ],
                    '4'
                ),
                (
                    'Equipo de protección personal (PPE en inglés) incluye:',
                    [
                        'Guantes',
                        'Mangas plásticas',
                        'Guardapolvos',
                        'Todos los de arriba',
                    ],
                    '5'
                ),
                (
                    'Cuando esté usando equipo de protección personal (PPE) uno debería:',
                    [
                        'Modificar el corte o estilo',
                        'Mantenerlo limpio y sin contaminarlo, y cambiarlo cuando se ensucie o se rasgue',
                        'Mantenerlo puesto hasta el fin de la jornada aunque estuviera contaminado',
                        'Ninguno de los de arriba',
                    ],
                    '6'
                ),
                (
                    'Cuántos pasos están incluidos en el procedimiento apropiado de lavarse las manos:',
                    [
                        'Siete',
                        'Cinco',
                        'Uno',
                        'Dos',
                    ],
                    '7'
                ),
                (
                    'Uno siempre debe lavarse las manos después de:',
                    [
                        'Usar el baño por cualquier razón',
                        'Tocar o rascarse cualquier parte de la piel, pelo, ojos, o boca',
                        'Comer, beber, o fumar',
                        'Todos los de arriba',
                    ],
                    '8'
                ),
                (
                    'La técnica apropiada de lavarse las manos debería incluir cual de las siguientes:',
                    [
                        'No se preocupe acerca de limpiarse sus uñas o entre los dedos',
                        'Usar la agua más fría que sea posible',
                        'Usando un jabón hermicida/antibacteriano o desinfectante que ha sido suministrado',
                        'Secarse las manos en su uniforme',
                    ],
                    '9'
                ),
                (
                    'Dónde se permiten almuerzos, bebidas, dulces, o chicle de mascar en las plantas de alimento:',
                    [
                        'En las áreas de proceso',
                        'Solamente en los comedores, lugares de descanso, o otras áreas de almacenaje designadas',
                        'En lugares donde se guarda la ropa o se cambia la ropa',
                        'Todos los de arriba',
                    ],
                    '10'
                )

            ]

haccp_sp = [
                (
                    'HACCP significa:',
                    [
                        'Análisis de Peligros y Puntos Criticos de Control (HACCP en inglés)',
                        'Ha Abierto Controles Con Peso',
                        'Hombres Avanzan Casi Cuando Pueden',
                        'Ninguno de los de arriba',
                    ],
                    '1'
                ),
                (
                    'El propósito de HACCP es:',
                    [
                        'Dar a usted más trabajo',
                        'Eliminar peligros potenciales de la comida para hacerla segura de comer',
                        'Limpiar el equipo apropiadamente',
                        'Ninguno de los de arriba',
                    ],
                    '2'
                ),
                (
                    'HACCP identifica qué tipo de peligro:',
                    [
                        'Biológico',
                        'Químico',
                        'Físico',
                        'Todos los de arriba',
                    ],
                    '3'
                ),
                (
                    'Cuál de las agencias del gobierno de EE.DU. requiere el HACCP:',
                    [
                        'El Departamento de Agricultura de Estados Unidos',
                        'La Administración de Alimentos y Drogas',
                        'Ambos (a ) y (b)',
                        'Ni (a) ni (b )',
                    ],
                    '4'
                ),
                (
                    'Cuántos principios de HACCP hay:',
                    [
                        'Cinco',
                        'Tres',
                        'Siete',
                        'Ocho',
                    ],
                    '5'
                ),
                (
                    'Cuál no es un principio de HACCP:',
                    [
                        'Análisis de Peligros',
                        'Equipo HACCP',
                        'Monitoreo',
                        'Mantenimiento de archivos',
                    ],
                    '6'
                ),
                (
                    'Cuál es un ejemplo de un peligro físico:',
                    [
                        'Vidrio',
                        'Químicos de limpieza',
                        'Bacterias',
                        'Ninguno de los de arriba',
                    ],
                    '7'
                ),
                (
                    'Cuál tipo de peligro es la causa de enfermedades provenientes de la comida:',
                    [
                        'Físico',
                        'Biológico',
                        'Químico',
                        'Ninguno de los de arriba',
                    ],
                    '8'
                ),
                (
                    'Un punto de control crítico (CCP) es:',
                    [
                        'Identificando los peligros y medidas de prevención',
                        'Un punto, paso, o procedimiento en el proceso de alimentos donde se puede controlar un peligro',
                        'Muestras y pruebas del producto',
                        'Todos los de arriba',
                    ],
                    '9'
                ),
                (
                    'Los archivos o registros de HACCP deben ser:',
                    [
                        'Precisos',
                        'Firmados',
                        'Fechados',
                        'Todos los de arriba',
                    ],
                    '10'
                )

            ]

sanitation_sp = [
                (
                    'Saneamiento se refiere a:',
                    [
                        'Solamente la limpieza del equipo y las áreas de producción de alimentos',
                        'Solamente la desinfección del equipo y las áreas de trabajo con alimentos',
                        'Todas las prácticas de procedimientos que se usan para mantener al lugar limpio y la comida producida sin contaminación',
                        'Limpieza y desinfección de las áreas de trabajo donde no hay alimentos',
                    ],
                    '1'
                ),
                (
                    'Cuál de los tópicos está relacionado a saneamiento:',
                    [
                        'Higiene y limpieza personal',
                        'Equipo y la ropa que se usa en el lugar de trabajo',
                        'Control de plagas',
                        'Todos los de arriba',
                    ],
                    '2'
                ),
                (
                    'Cuál no requiere que se sigan procedimientos de saneamiento estrictos:',
                    [
                        'Equipo de producción de alimentos',
                        'Automóviles de los empleados',
                        'Producción de alimentos en las áreas de trabajo',
                        'La higiene personal de los empleados',
                    ],
                    '3'
                ),
                (
                    'El residuo de la comida que queda en el equipo es:',
                    [
                        'Una fuente de alimento para las bacterias',
                        'Una fuente de contaminación quimica',
                        'No importa, no necesita ser limpiado',
                        'Todos los de arriba',
                    ],
                    '4'
                ),
                (
                    'Cuántos pasos existen en el procedimiento basico de limpieza y desinfección:',
                    [
                        'Uno',
                        'Dos',
                        'Tres',
                        'Cuatro',
                    ],
                    '5'
                ),
                (
                    'Los pasos básicos de limpieza y desinfección incluyen:',
                    [
                        'Limpieza inicial',
                        'Limpieza con un quimico',
                        'Desinfección',
                        'Todos los de arriba',
                    ],
                    '6'
                ),
                (
                    'Los metodos para aplicar químicos de limpieza y desinfección incluyen:',
                    [
                        'Mezclarlos con agua y aplicarlos con un cepillo',
                        'Medir y aplicarlo por medio de una manguera',
                        'Aplicarlos como una espuma',
                        'Todos los de arriba',
                    ],
                    '7'
                ),
                (
                    'El equipo de limpieza e higiene y los químicos deben ser:',
                    [
                        'Puestos donde quiera en la planta después de usarlos',
                        'Usarlos, manejarlos, y almacenarlos apropiadamente',
                        'Guardarlos cuando todavía esten mojados',
                        'Ninguno de los de arriba',
                    ],
                    '8'
                ),
                (
                    'Cuando esté almacenando equipo de limpieza y desinfección, asegúrese que:',
                    [
                        'Limpie el equipo después de cada uso',
                        'Seque el equipo completamente antes de guardarlo',
                        'Almacene el equipo sólo en un área de almacenaje designada',
                        'Todos los de arriba',
                    ],
                    '9'
                ),
                (
                    'Cuando use químicos de limpieza y desinfección siempre:',
                    [
                        'Lea y siga con cuidado las instrucciones de la etiqueta',
                        'Hágalo de cualquier manera que usted lo desee',
                        'Use tan poco o mucho silo desea',
                        'Ninguno de los de arriba',
                    ],
                    '10'
                )

            ]

time_sp = [
                (
                    'La temperatura de "zona de peligro" está entre:',
                    [
                        '20 y 120 °F',
                        '30 y 130 °F',
                        '40y140 °F',
                        '50 y 150 °F',
                    ],
                    '1'
                ),
                (
                    'Los controles de tiempo y temperatura se usan para apropiadamente:',
                    [
                        'Cocinar comida',
                        'Enfriar comida',
                        'Almacenar comida',
                        'Todos los de arriba',
                    ],
                    '2'
                ),
                (
                    'Los controles de tiempo y temperatura incluyen :',
                    [
                        'Cocinar',
                        'Congelar',
                        'Pasteurizar',
                        'Todos los de arriba',
                    ],
                    '3'
                ),
                (
                    'El propósito de los controles de tiempo y temperatura es para:',
                    [
                        'Producir la comida más rápidamente',
                        'Controlar el crecimiento de bacterias potencialmente peligrosas',
                        'Crear un entorno caliente, húmedo',
                        'Hacer que la comida sepa bien',
                    ],
                    '4'
                ),
                (
                    'Cuál de las bacterias pueden controlarse por tiempo y temperatura:',
                    [
                        'Listeria',
                        'E. coli',
                        'Salmonela',
                        'Todos los de arriba',
                    ],
                    '5'
                ),
                (
                    'Cuál es el control de tiempo y temperatura que se usa más comúnmente en el procesamiento de comida:',
                    [
                        'Cocinar',
                        'Irradiar',
                        'Procesar térmicamente',
                        'Todos los de arriba',
                    ],
                    '6'
                ),
                (
                    'Enfriando los alimentos cerca a 40 grados Fahrenheit se llama:',
                    [
                        'Congelar',
                        'Pasteurizar',
                        'Refrigerar',
                        'Todos los de arriba',
                    ],
                    '7'
                ),
                (
                    'La primera regla a seguirse en los controles de tiempo y temperatura es:',
                    [
                        'Estar cerca del punto, es suficiente',
                        'Siempre siga los procedimientos y prácticas establecidos en su companía para los alimentos que está elaborando',
                        'Si hace un pequeño error, no importa mayormente',
                        'Ninguno de los de arriba',
                    ],
                    '8'
                ),
                (
                    'Para asegurarse que se ha conformado a los controles correctos de tiempo y temperatura:',
                    [
                        'Mantenga las puertas cerradas para refrigeradoras, congeladoras, lugares de sostén, depósitos, recintos de proceso, y otras áreas de trabajo enfriadas',
                        'Nunca altere el tiempo especificado para calentar, blanquear, cocinar, o enfriar un producto',
                        'Use un termómetro para verificar si la comida ha llegado a su temperatura de proceso correcta',
                        'Todos los de arriba',
                    ],
                    '9'
                ),
                (
                    'Si usted piensa que se ha violado un control de tiempo y temperatura:',
                    [
                        'Digale a su supervisor o persona de control de calidad, de manera que pueda comprobar un lote o hacer una decision en lo que debería seguirse',
                        'Deseche el lote cuando nadie esté mirando',
                        'No le diga a nadie',
                        'Ninguno de los de arriba',
                    ],
                    '10'
                )

            ]

foreign_sp = [
                (
                    'La detección de materia foránea es:',
                    [
                        'Encontrar objetos en su café mañanero antes de ir a trabajar',
                        'Localizar objetos en la comida que no deberían estar ahí',
                        'Desinfectar el equipo y áreas de! trabajo de alimentos',
                        'Ninguno de las de arriba',
                    ],
                    '1'
                ),
                (
                    'La detección de materia foránea es importante porque:',
                    [
                        'Ayuda a garantizar que los productos no contengan objetos extraños',
                        'Es la seguridad de trabajo para los empleados',
                        'Ayuda a detectar bacterias',
                        'Ninguno de los de arriba',
                    ],
                    '2'
                ),
                (
                    'La materia foránea puede venir de:',
                    [
                        'Materia prima',
                        'Dentro de la planta',
                        'Empleados',
                        'Todos los de arriba',
                    ],
                    '3'
                ),
                (
                    'Los tipos de materias foráneas incluyen:',
                    [
                        'Metal',
                        'Vidrio',
                        'Madera',
                        'Todos los de arriba',
                    ],
                    '4'
                ),
                (
                    'Prácticas de higiene personal incorrectas son la causa de cuáles tipos de contaminantes:',
                    [
                        'Chicle',
                        'Pelo',
                        'Joyería',
                        'Todos los de arriba',
                    ],
                    '5'
                ),
                (
                    'Es importante conducir detección de materias foráneas:',
                    [
                        'Cuando se recibe la materia prima y cuando la comida está poco antes de salir de la planta',
                        'Durante el proceso de cocinarla',
                        'Después de que la comida ha llegado a la tienda',
                        'Todos los de arriba',
                    ],
                    '6'
                ),
                (
                    'Materia prima que entra puede contener materia foráneas:',
                    [
                        'Plagas',
                        'Tierra',
                        'Basura',
                        'Todos los de arriba'
                    ],
                    '7'
                ),
                (
                    'Cuál equipo se usa para detectar materia foráneas:',
                    [
                        'Un termometro',
                        'Imanes y detectores de metal',
                        'Un refrigerador',
                        'Ninguno de los arriba',
                    ],
                    '8'
                ),
                (
                    'Las inspeccion visual significa:',
                    [
                        'Mirando a traves de un lente de aumento',
                        'Usando imanes y detectores de metal',
                        'Buscando materias foráneas a ojo pelado',
                        'Ninguno de los de arriba',
                    ],
                    '9'
                ),
                (
                    'Cuál medida de control ayuda a evitar que las materias foráneas se metan a la comida:',
                    [
                        'Buenas prácticas de higiene personal',
                        'Inspeccion de materia prima antes de añadirla a la comida',
                        'Medidas de buen orden en sitio',
                        'Todos los de arriba'
                    ],
                    '10'
                )

            ]

cross_sp = [
                (
                    'La contaminación entrecruzada es:',
                    [
                        'Contaminación de la comida con cruces',
                        'Contaminación de comida con otros materiales',
                        'Contaminación de comida con ingredientes',
                        'Ninguna de las respuestas de arriba',
                    ],
                    '1'
                ),
                (
                    'Cuál no puede ser un contaminante posible:',
                    [
                        'Pesticidas',
                        'Madera',
                        'Bacteria',
                        'Rayos de luna',
                    ],
                    '2'
                ),
                (
                    'Contaminantes químicos incluyen:',
                    [
                        'Agua',
                        'Químicos de limpieza',
                        'Leche',
                        'Todos los de arriba',
                    ],
                    '3'
                ),
                (
                    'Para evitar la contaminación entrecruzada siempre :',
                    [
                        'Almacene los quimicos en su lugar designado cuando no se usen',
                        'Garantice que las áreas de producción de alimentos esten limpias, bien enjaguadas, y libres de residuo quimico después de desinfección',
                        'Ponga comida y materiales de empaque lejos o cúbralos antes de limpiar o aplicar pesticidas',
                        'Todos los de arriba',
                    ],
                    '4'
                ),
                (
                    'Las bacterias pueden contaminar los alimentos dándose un aventón en:',
                    [
                        'Gente',
                        'Equipo',
                        'Materiales de empaque',
                        'Todos los de a rriba',
                    ],
                    '5'
                ),
                (
                    'Para impedir la contaminación entrecruzada bacteriana siempre:',
                    [
                        'Lávese las manos',
                        'Use lavados de pies y estaciones para desinfectar las manos',
                        'Separe los productos crudos y cocinados',
                        'Todos los de arriba',
                    ],
                    '6'
                ),
                (
                    'Peligros físicos incluyen:',
                    [
                        'Metal',
                        'Polvo',
                        'Personas',
                        'Agua',
                    ],
                    '7'
                ),
                (
                    'Payasadas incluyen:',
                    [
                        'Manejo de un montacargas imprudentemente',
                        'Usando mangueras para mojar los compañeros',
                        'Tirar comida',
                        'Todos los de arriba',
                    ],
                    '8'
                ),
                (
                    'Qué no se usa para detector la contaminación entrecruzada en la comida:',
                    [
                        'Un detector de metal',
                        'Un destornillador',
                        'Una inspección visual',
                        'Mallas y escudriñadores',
                    ],
                    '9'
                ),
                (
                    'La contaminación entrecruzada ocurre cuando:',
                    [
                        'No se obedecen las reglas',
                        'Las medidas de control son inadecuadas',
                        'Hay un error o accidente humano',
                        'Todos los de arriba',
                    ],
                    '10'
                )

            ]

allergens_sp = [
                (
                    'Una reacción alérgica a los alimentos es causada por:',
                    [
                        'Comer demasiada comida',
                        'La reacción del cuerpo a una proteína foránea',
                        'Una reacción a bacterias peligrosas en la comida',
                        'Todo lo de arriba',
                    ],
                    '1'
                ),
                (
                    'Las personas que tienen alérgias generalmente sufren de:',
                    [
                        'Vómito',
                        'Urticaria',
                        'Dificultad en respirar',
                        'Todo lo de arriba',
                    ],
                    '2'
                ),
                (
                    'Alérgenos alimenticios comunes incluyen:',
                    [
                        'Cacahuates (maní)',
                        'Leche',
                        'Pescado',
                        'Todo lo de arriba',
                    ],
                    '3'
                ),
                (
                    'La única manera de dar tratamiento a los alérgenos alimenticios es:',
                    [
                        'Recibir una inyección',
                        'Recostar se y descansar',
                        'Evitar comidas que ca usen la reacción alérgica',
                        'Ninguna de las respuestas de arriba',
                    ],
                    '4'
                ),
                (
                    'Los alérgenos de los alimentos pueden contaminar los productos por:',
                    [
                        'uso inapropiado de los ingredientes',
                        'utilización de ingredientes usados anteriormente (reprocesados)',
                        'limpieza o higiene inapropiada del equipo',
                        'Todo lo de arriba',
                    ],
                    '5'
                ),
                (
                    'Para evitar contaminación accidental de ingredientes con alérgenos:',
                    [
                        'Chequee embarques de ingredientes y materia prima recibidos',
                        'Almacene ingredientes alérgenicos separándolos de otros ingredientes',
                        'Siempre chequee los ingredientes antes de que se los añada a un lote de alimentos.',
                        'Todo lo de arriba',
                    ],
                    '6'
                ),
                (
                    'Para evitar la contaminación de alérgenos cuando se procesen productos, uno debería:',
                    [
                        'Inspeccionar visualmente el equipo para determinar que no haya residuo o acumulación de alérgenos provenientes de producciones anteriores, antes de comenzar a procesar otro producto.',
                        'Usar equipo separado, o codificado a color, para productos que contengan un alérgeno conocido',
                        'Añadir el ingrediente alérgeno cerca del fin del proceso',
                        'Todo lo de arriba',
                    ],
                    '7'
                ),
                (
                    'El reproceso que contengan alérgenos usados anteriormente se debe:',
                    [
                        'Etiquetar así con claridad',
                        'Utilizar sólo en productos compatibles',
                        'Ambas a. y b.',
                        'Ni a, nib.',
                    ],
                    '8'
                ),
                (
                    'La limpieza apropiada que sigue al procesamiento de productos que contengan alérgenos quizas puede incluir:',
                    [
                        'Desarmar el equipo',
                        'Limpiar lugares y partes del equipo a mano',
                        'Visualmente inspeccionar el equipo después de limpiarlo',
                        'Todo lo de arriba',
                    ],
                    '9'
                ),
                (
                    'Cuando se trabaja con comidas que contiene alérgenos, uno siempre debería:',
                    [
                        'Seguir todas las reglas de seguridad de la compañía',
                        'Trabajar lo más rapidamente posible',
                        'Evitar contacto con los compañeros',
                        'Todo lo de arriba',
                    ],
                    '10'
                )

            ]

pest_sp = [
                (
                    'Las plagas incluyen cuáles de las siguientes:',
                    [
                        'Insectos',
                        'Pájaros',
                        'Roedores',
                        'Todos los de arriba',
                    ],
                    '1'
                ),
                (
                    'El control de plagas es parte de cuál programa de su compania:',
                    [
                        'Programa de higiene',
                        'Mantenimiento del equipo',
                        'Pruebas microbiológicas',
                        'Ninguno de los e arriba',
                    ],
                    '2'
                ),
                (
                    'A las plagas les atrae:',
                    [
                        'Comida',
                        'Agua',
                        'Basura',
                        'Todos los de arriba',
                    ],
                    '3'
                ),
                (
                    'La mejor manera de combatir plagas es:',
                    [
                        'Combatirlas una vez que estén dentro de la planta',
                        'Mantenerlas fuera de la planta de alimentos desde un principio',
                        'Detectarlas una vez que estén en el producto comestible',
                        'Ninguno de los de arriba',
                    ],
                    '4'
                ),
                (
                    'Para mantener las plagas afuera:',
                    [
                        'La planta tiene que estar bien sellada',
                        'Eliminar fuentes de comida y agua',
                        'Mantener las puertas y ventanas cerradas',
                        'Todos los de arriba',
                    ],
                    '5'
                ),
                (
                    'Los métodos de control de insectos incluye:',
                    [
                        'Insecticidas',
                        'Aparatos para electrocutar insectos ("zappers")',
                        'Esterilización por medio de calor',
                        'Todos los de arriba',
                    ],
                    '6'
                ),
                (
                    'Los métodos que se usan para aplicar pesticidas incluye:',
                    [
                        'Hacer neblina con químicos',
                        'Fumigación',
                        'Rocío de grietas y hendeduras',
                        'Todos los de arriba',
                    ],
                    '7'
                ),
                (
                    'El método principal de control de plagas es:',
                    [
                        'Cebar',
                        'Atrapar',
                        'Ambas (a) y (b)',
                        'Ninguno, ni (a) ni (b)',
                    ],
                    '8'
                ),
                (
                    'Una regla general que usted puede seguir para apoyar el control de roedores por medio de cebar incluye:',
                    [
                        'Usándolo solamente en áreas designadas y autorizadas',
                        'Inspeccionando y cambiando los cebos frecuentemente',
                        'Disponiendo, o notificando a la persona apropiada que deseche cualquier cuerpo de roedor que se encuentre',
                        'Todos los de arriba',
                    ],
                    '9'
                ),
                (
                    'Cuál no es un ejemplo de un buen control de plagas:',
                    [
                        'Limpieza de los derrames',
                        'Dejando las puertas y ventanas abiertas',
                        'Limpieza de basura',
                        'Usando pesticidas',
                    ],
                    '10'
                )

            ]

security_sp =[
                (
                    'Los riesgos de seguridad en su compania puede incluir:',
                    [
                        'Robo',
                        'Asalto',
                        'Vandalismo',
                        'Todos los de arriba',
                    ],
                    '1'
                ),
                (
                    'Los parques de estacionamiento pueden ser peligrosos porque:',
                    [
                        'Hay patrones de trafico que no se pueden anticipar',
                        'Choferes descuidados',
                        'Lugares escondidos que pueden encubrir a criminales',
                        'Todos los de arriba',
                    ],
                    '2'
                ),
                (
                    'Cuando entra en un parque de estacionamiento, usted debería estacionarse:',
                    [
                        'Donde puede ver claramente alrededor de su vehículo',
                        'Donde le pueda ser visto',
                        'Cerca de la entrada, si es posible',
                        'Todos los de arriba',
                    ],
                    '3'
                ),
                (
                    'Si hay otra persona detrás suyo que desea entrar al edificio, usted debería:',
                    [
                        'Dejarles entrar si los conoce',
                        'Insistir que usen su propia placa de identificación para que lo escanean para entrar al edificio',
                        'Verificar sus placas de identificación para ver que sea el dueño de la placa, y luego permitirle entrar',
                        'Todos los de arriba',
                    ],
                    '4'
                ),
                (
                    'Un lugar en la planta que debe mantenerse segura es:',
                    [
                        'Almacén',
                        'Área de producción',
                        'Laboratorio',
                        'Todos los de arriba',
                    ],
                    '5'
                ),
                (
                    'Para proteger el producto mientras trabaja, usted debería:',
                    [
                        'Asegurarse que los detectores de metal, imanes, etc. estén funcionando apropiadamente.',
                        'Apropiadamente etiquetar y el producto que se reprosesa',
                        'Reportar cualquier existencia faltante',
                        'Todos los de arriba',
                    ],
                    '6'
                ),
                (
                    'Para protegerse mientras trabaje, usted debería:',
                    [
                        'Reportar actividades sospechosas',
                        'Reportar ventanas y candados rotos',
                        'Estar consciente de todo a su alrededor todo el tiempo',
                        'Todo lo de arriba',
                    ],
                    '7'
                ),
                (
                    'No traiga contenedor de almuerzo o bolsas dentro de producción porque:',
                    [
                        'No hay espacio para estos en su lugar de trabajo',
                        'Estos podrian usarse para esconder químicos, armas, y aparatos explosivos',
                        'Otros empleados pueden adueñarse de su comida',
                        'Ninguno de los de arriba',
                    ],
                    '8'
                ),
                (
                    'Actividades sospechosas incluyen:',
                    [
                        'Actitud nerviosa, angustiada, o sigilosa',
                        'Tomar fotos de las áreas y equipo de trabajo',
                        'Actitud amenazante a las personas',
                        'Todos los de arriba',
                    ],
                    '9'
                ),
                (
                    'Visitantes a su compania deberían:',
                    [
                        'Registrarse antes de que entren y caminen dentro de su compania',
                        'Llevar puesta alguna forma de identificación',
                        'Caminar con el empleado a quien han venido a visitar',
                        'Todos los de arriba',
                    ],
                    '10'
                )

            ]

fltv = [
        (
            'Forklift inspections are only required once per year.',
            [
                'True',
                'False'
            ],
            '1'
        ),
        (
            'A forklift will tip over if the center of gravity is outside the stability triangle.',
            [
                'True',
                'False'
            ],
            '2'
        ),
        (
            'OSHA requires retraining at least every 3 years.',
            [
                'True',
                'False'
            ],
            '3'
        ),
        (
            'The safest way to cross a railroad track is at an angle.',
            [
                'True',
                'False'
            ],
            '4'
        ),
        (
            'If the forklift does not have a seatbelt then it is not required on that particular model.',
            [
                'True',
                'False'
            ],
            '5'
        ),
        (
            'Forklifts are designed to handle loads of any size and weight.',
            [
                'True',
                'False'
            ],
            '6'
        ),
        (
            'Driving with an obstructed view is allowed if it is only within 10 yards.',
            [
                'True',
                'False'
            ],
            '7'
        ),
        (
            'Although forklift injuries are common, no one has ever been killed in a forklift accident.',
            [
                'True',
                'False'
            ],
            '8'
        ),
        (
            'Maximum safe speed should be equivalent to around 20 miles per hour.',
            [
                'True',
                'False'
            ],
            '9'
        ),
        (
            'It is okay to give someone in management a ride if the walk is more than 200 yards.',
            [
                'True',
                'False'
            ],
            '10'
        ),
        (
            'No person is allowed to pass underneath a raised load.',
            [
                'True',
                'False'
            ],
            '11'
        ),
        (
            'If the load is too heavy or too far from the fulcrum the forklift will tip forward.',
            [
                'True',
                'False'
            ],
            '12'
        ),
        (
            'The “Load Center” is the sensor on the forklift that warns if the load is too heavy.',
            [
                'True',
                'False'
            ],
            '13'
        ),
        (
            'Without a load a forklift can never tip over.',
            [
                'True',
                'False'
            ],
            '14'
        ),
        (
            'If a forklift begins to tip over you should quickly jump away from the forklift and falling items.',
            [
                'True',
                'False'
            ],
            '15'
        ),
        (
            'Driving across a slope or angle could cause the forklift to tip over.',
            [
                'True',
                'False'
            ],
            '16'
        ),
        (
            'When transporting a load on a slope, always keep the forks pointed downhill.',
            [
                'True',
                'False'
            ],
            '17'
        ),
        (
            'Forks should be lowered to the ground when the operator is more than 25 feet away.',
            [
                'True',
                'False'
            ],
            '18'
        ),
        (
            'Battery charging should only be done in designated areas.',
            [
                'True',
                'False'
            ],
            '19'
        ),
        (
            'Lifting an employee on the forks is approved only if your supervisor is watching',
            [
                'True',
                'False'
            ],
            '20'
        )
    ]

fltv_sp = [
        (
            'El montacargas requiere inspección sólo una vez al año.',
            [
                'Verdad',
                'Falso'
            ],
            '1'
        ),
        (
            'Un montacargas se volcará si el centro de gravedad está fuera del triángulo de estabilidad.',
            [
                'Verdad',
                'Falso'
            ],
            '2'
        ),
        (
            'OSHA exige volver a capacitarse al menos cada tres años.',
            [
                'Verdad',
                'Falso'
            ],
            '3'
        ),
        (
            'La manera más segura de cruzar rieles ferroviarios es en ángulo.',
            [
                'Verdad',
                'Falso'
            ],
            '4'
        ),
        (
            'Si el montacargas no tiene cinturón de seguridad es porque no necesita ese modelo en particular.',
            [
                'Verdad',
                'Falso'
            ],
            '5'
        ),
        (
            'Los montacargas están diseñados para maniobrar cargas de cualquier tamaño y peso.',
            [
                'Verdad',
                'Falso'
            ],
            '6'
        ),
        (
            'Se permite conducir con obstrucción visual sólo si es una distancia corta.',
            [
                'Verdad',
                'Falso'
            ],
            '7'
        ),
        (
            'Aunque las lesiones con montacargas son comunes, nadie ha muerto nunca en un accidente de montacargas.',
            [
                'Verdad',
                'Falso'
            ],
            '8'
        ),
        (
            'La velocidad máxima segura equivaldría alrededor de 20 millas por hora.',
            [
                'Verdad',
                'Falso'
            ],
            '9'
        ),
        (
            'Está bien llevar a un administrador como pasajero si el recorrido es mayor de 200 yardas.',
            [
                'Verdad',
                'Falso'
            ],
            '10'
        ),
        (
            'No se permite a nadie pasar por debajo de una carga levantada.',
            [
                'Verdad',
                'Falso'
            ],
            '11'
        ),
        (
            'Si la carga es demasiado pesada o está muy lejos del punto de apoyo el montacargas se inclinará hacia delante.',
            [
                'Verdad',
                'Falso'
            ],
            '12'
        ),
        (
            'El “centro de carga” es un detector del montacargas que le advierte si la carga es demasiado pesada.',
            [
                'Verdad',
                'Falso'
            ],
            '13'
        ),
        (
            'Sin carga un montacargas nunca puede volcarse.',
            [
                'Verdad',
                'Falso'
            ],
            '14'
        ),
        (
            'Si un montacargas empieza a volcarse usted debe rápidamente saltar fuera del montacargas y de los objetos que caen.',
            [
                'Verdad',
                'Falso'
            ],
            '15'
        ),
        (
            'Manejar a través de una pendiente o en ángulo puede ocasionar un vuelco del montacargas.',
            [
                'Verdad',
                'Falso'
            ],
            '16'
        ),
        (
            'Cuando transporte una carga por una pendiente, mantenga siempre las horquillas apuntando cuesta abajo.',
            [
                'Verdad',
                'Falso'
            ],
            '17'
        ),
        (
            'Las horquillas deben bajarse al suelo cuando el operador se aleja a más de 25 pies.',
            [
                'Verdad',
                'Falso'
            ],
            '18'
        ),
        (
            'La carga de la batería debe hacerse sólo en áreas designadas.',
            [
                'Verdad',
                'Falso'
            ],
            '19'
        ),
        (
            'Levantar a un empleado en el montacargas está aprobado sólo si su supervisor está vigilando.',
            [
                'Verdad',
                'Falso'
            ],
            '20'
        )
    ]

wps = [
        (
            'One aspect of proper lifting techniques means that you:',
            [
                'Hold the load as far from your body as possible',
                'Get help with larger loads',
                'Bend your back and keep your knees straight',
                'Twist your back slowly if you need to turn while lifting',
            ],
            '1'
        ),
        (
            'Housekeeping is essential to a safe workplace because:',
            [
                'It shows you take pride in your work',
                'It makes your job easier',
                'It saves your company money',
                'Clutter and improperly stored materials are a safety and fire hazard',
            ],
            '2'
        ),
        (
            'Lockout/tagout devices must be attached by:',
            [
                'The machine operator',
                'The authorized employee or his helper',
                'The authorized employee',
                'The machine operator or a supervisor',
            ],
            '3'
        ),
        (
            'Your company must have a safety data sheet (or SDS) for each chemical that poses a physical or health hazard at your workplace.',
            [
                'True',
                'False',
            ],
            '4'
        ),
        (
            'Protecting an extension cord while you work helps prevent damage that can cause electric shock.  This includes:',
            [
                'Stapling the cord to secure it in place',
                'Leaving slack in the cord when you use the tool',
                'Running the cord under carpet to protect it from foot traffic',
                'All of the above',
            ],
            '5'
        ),
        (
            'The best defense against a fire is to:',
            [
                'Know how to use a fire extinguisher',
                'Know the different classes of fire extinguishers',
                'Know how to prevent fires in the first place',
                'Know where your headcount area is located',
            ],
            '6'
        ),
        (
            'When a pedestrian encounters a forklift, the right-of-way goes to:',
            [
                'The forklift',
                'The forklift, if it gets to the intersection first',
                'The forklift, if it’s approaching from the right',
                'The pedestrian',
            ],
            '7'
        ),
        (
            'If a power tool has a safety guard, you must:',
            [
                'Remove the guard just before using the tool',
                'Never remove the safety guard when using the tool',
                'Contact the tool manufacturer to see if the guard is really necessary',
                'Carry the tool by the cord or hose',
            ],
            '8'
        ),
        (
            'When climbing a ladder, you should:',
            [
                'Face the ladder',
                'Use one hand to grasp the ladder',
                'Carry any object or load, as long as it doesn’t affect your balance',
                'All of the above',
            ],
            '9'
        ),
        (
            'Universal precautions are:',
            [
                'A method of selecting appropriate PPE when a bloodborne pathogen incident occurs',
                'A system of seven steps to follow when cleaning up machinery following an incident',
                'An approach to infection control that considers all blood and body fluids to be infectious',
                'None of the above',
            ],
            '10'
        )

    ]

wps2 = [
        (
            '_________________ responsible for providing you with a safe workplace.',
            [
                'OSHA is',
                'Your employer is',
                'Your co-workers are',
                'You are',
            ],
            '11'
        ),
        (
            '_______________ ultimately responsible for my personal safety.',
            [
                'I am',
                'My employer is',
                'OSHA is',
                'My co-workers are',
            ],
            '12'
        ),
        (
            'Ergonomics is a method of:',
            [
                'Achieving higher productivity',
                'Making the workstation and work fit your body',
                'Reaching a team consensus',
                'Calculating workers’ compensation costs',
            ],
            '13'
        ),
        (
            'Simple movements can cause injuries if they are repeated enough.',
            [
                'True',
                'False',
            ],
            '14'
        ),
        (
            'When planning your route before you lift, you should make sure:',
            [
                'You have a map of the route you’re taking',
                'Your path is clear of slipping and tripping hazards',
                'You put on proper PPE',
                'The load meets OSHA requirements',
            ],
            '15'
        ),
        (
            'You can size up a load before you lift it by:',
            [
                'Carrying the load to a scale and weighing it',
                'Asking someone else if they think it’s too heavy for you to lift',
                'Testing the weight by moving one of the corners',
                'None of the above',
            ],
            '16'
        ),
        (
            'Which of the following is a proper lifting technique to use:',
            [
                'Bend at the waist',
                'Carry the load away from your body',
                'Bend at the knees',
                'Lift slowly and let your back do the work',
            ],
            '17'
        ),
        (
            'Proper housekeeping procedures include:',
            [
                'Clean up spills right away',
                'Clean up grease and oil immediately',
                'Remove ice and snow',
                'All of the above',
            ],
            '18'
        ),
        (
            'Good housekeeping prevents accidents and injuries because it:',
            [
                'Creates a pleasant work environment',
                'Keeps work areas free of materials and obstructions that can cause hazards',
                'Provides exercise by bending over to pick up debris',
                'Presents a good company image',
            ],
            '19'
        ),
        (
            'Lockout is required:',
            [
                'During servicing and maintenance where unexpected start up of equipment could harm employees',
                'During repair, renovation and replacement work',
                'During modifications and adjustments to powered equipment',
                'All of the above',
            ],
            '20'
        ),
        (
            'Lockout/Tagout is required when you:',
            [
                'Stop the machine at the end of a normal shift',
                'Unplug a drill to change a drill bit',
                'Remove a machine guard to clear a jam',
                'None of the above',
            ],
            '21'
        )
    ]
