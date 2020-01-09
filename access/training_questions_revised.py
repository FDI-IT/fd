#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
# # gbpp
# def convert_to_ordered(dic):
#     # return sorted(dict)
#     keys = sorted(dic.keys())
#     # return OrderedDict((d, True) for d in dict)
#     ordered = OrderedDict()
#     for k in keys:
#         ordered[k] = dic[k]
#     return ordered


wiki = [
    (
        'Any sign of tampering of product or equipment you should alert',
        {
            'text':''
        },
        'text'
    ),
    (
        'If you see any suspicious criminal activity, alert the manager who will alert',
        {
            'text':''
        },
        'text'
    ),
    (
        'Outside contractors in unauthorized areas or if you receive unexpected mail or packages alert',
        {
            'text':''
        },
        'text'
    ),
    (
        'Truckers are the only people other than employees and routine outside contractors (Once signed in) that can enter the side doors',
        OrderedDict([('True' ,'True',),('False','False')]),
        # {
        #     'True' :'True',
        #     'False':'False'
        # },
        'radio'
    ),
    (
        'Truckers can use the men’s locker room lavatories?',
        OrderedDict([('True' ,'True',),('False','False')]),
        'radio'
    ),
    (
        'Any government inspector can review a record as long as they show a badge',
        OrderedDict([('True' ,'True',),('False','False')]),
        'radio'
    ),
    (
        'Any non-personal visitor coming into the building must sign a secrecy agreement for the first time.',
        OrderedDict([('True' ,'True',),('False','False')]),
        'radio'
    ),

]

# colorblind
#
hazcom = [
    # links to appropriate labels/sds
    (
        ''
    ),
    # questions
    (
        'Name of product?',
        'Is it hazardous?',
        'What are the hazards?',
        'Are there any signal words?',
        'What are the precautionary statements?',
    )
]
#
fooddefense = [
    (   'What types of suspicious activity should be reported to your supervisor?',
        {
            'a':'Entry from doors by unauthorized individuals',
            'b':'Addition of contaminants',
            'c':'Adulteration of raw materials or packaging before receipt',
            'd':'All of the above'
        }
    ),
    (
        'What steps would we use to approve a new supplier?',
        {
            'a':'Phone interview by our lab',
            'b':'Word of mouth from other flavor companies',
            'c':'Completing our provided questonnaires',
            'd':'Taking our online survey',
        }
    ),
    (
        'Where can a trucker go?',
        {
            'a':'Anywhere they would like',
            'b':'Restroom and warehouse behind the white line',
            'c':'Loading area and front office',
            'd':'Non-production areas',
        }
    ),
    (
        'Contractors may enter the building after signing in, wearing a badge and being escorted to the thing they are working on.',
        OrderedDict([('True' ,'True',),('False','False')]),
    ),
    (
        'Unfinished batches may be left until the next day as long as they are stored correctly',
        OrderedDict([('True' ,'True',),('False','False')]),
    )

]

#
# ccp = [()]
#
# fltv




bacteria = [
    (   'Bacteria are:',
        {
            'a':'Living organisms so small they can only be seen with the help of a microscope',
            'b':'Living organisms large enough to be seen with the naked eye',
            'c':'Organisms that are made of "micros"',
            'd':'None of the above'
        },
    ),
    (
        'Bacteria are found in:',
        {
            'a':'Food',
            'b':'Soil',
            'c':'Intestines of people and animals',
            'd':'All of the above'
        },

    ),
    (
        'Bacteria are used to make:',
        {
            'a':'Bread',
            'b':'Cheese',
            'c':'Summer sausage',
            'd':'All of the above'
        },

    ),
    (
        'Which is not a harmful bacteria:',
        {
            'a':'Listeria',
            'b':'E. coli',
            'c':'Zoology',
            'd':'Salmonella'
        },

    ),
    (
        'Disease caused by harmful bacteria is called:',
        {
            'a':'Microbial poisioning',
            'b':'Foodborne illness',
            'c':'Food contamination',
            'd':'food infection'
        },

    ),
    (
        'A common symptom of ma ny food borne illnesses include:',
        {
            'a':'Vomiting',
            'b':'Blindess',
            'c':'Sleepiness',
            'd':'None of the above'
        },

    ),
    (
        'A procedure food companies use to try to control bacteria is:',
        {
            'a':'Refrigeration',
            'b':'Cleaning and sanitizing',
            'c':'Cooking',
            'd':'All of the above'
        },

    ),
    (
        'The most important personal hygiene practice to control the spread of bacteria is:',
        {
                'a':'Wearing hair restraints',
                'b':'Washing your hands',
                'c':'Bathing daily',
                'd':'None of the above'
        },

    ),
    (
        'Spoilage bacteria can cause food to become:',
        {
            'a':'Mushy',
            'b':'Slimy',
            'c':'Smelly',
            'd':'All of the above'
        },

    ),
    (
        'Ways to prevent the contamination of and control bacteria in food include:',
        {
            'a':'Time and temperature controls',
            'b':'Sanitation',
            'c':'Moisture control',
            'd':'All of the above'
        },

    )
]

foodborne = [
    (
        'Foodborne illness affects how many people each year:',
        {
            'a':'76,000',
            'b':'760,000',
            'c':'76,000,000',
            'd':'None of the above'
        },

    ),
    (
        'Foodborne illness kills how many people each year:',
        {
            'a':'500',
            'b':'5,000',
            'c':'50,000',
            'd':'None of the above'
        },

    ),
    (
        'Foodborne illnesses have been conquered due to improvements in food safety, such as:',
        {
            'a':'Pasteurization of milk',
            'b':'Safe canning',
            'c':'Disinfection of water supplies',
            'd':'All of the above'
        },

    ),
    (
        'New microorganisms emerge as public health problems because:',
        {
            'a':'Microorganisms can evolve',
            'b':'Our environment and the way we live are changing',
            'c':'Food production practices and consumption habits change',
            'd':'All of the above'
        },

    ),
    (
        'When harmful microorganisms are swallowed, they:',
        {
            'a':'Stay in the intestine',
            'b':'Produce a toxin',
            'c':'Invade deep body tissues',
            'd':'All of the above'
        },

    ),
    (
        'Symptoms of food borne illness include:',
        {
            'a':'Diarrhea',
            'b':'Stomach cramps',
            'c':'Nausea',
            'd':'All of the above'
        },

    ),
    (
        'Contaminated food can be very dangerous, especially to:',
        {
            'a':'Pregnant women',
            'b':'Small children',
            'c':'The elderly',
            'd':'All of the above'
        },

    ),
    (
        'Treatment of foodborne illness typically requires you to:',
        {
            'a':'Eat healthy foods',
            'b':'Get a shot',
            'c':'Drink lots of fluids',
            'd':'None of the above'
        },

    ),
    (
        'Food can become contaminated by:',
        {
            'a':'Infected employees',
            'b':'Cross contamination',
            'c':'Neither a nor b',
            'd':'Both a and b'
        },

    ),
    (
        'Many foodborne illnesses can be prevented by:',
        {
            'a':'Practicing good personal hygiene',
            'b':'Properly cleaning and sanitizing equipment and work areas',
            'c':'Following time and temperature controls',
            'd':'All of the above'
        },

    )
]

personalhygiene = [
    (
        'Personal hygiene is:',
        {
            'a':'Keeping yourself clean',
            'b':'Sanitizing of equipment and food work areas',
            'c':'Coming to work on time',
            'd':'None ofthe above'
        },

    ),
    (
        'Which is not a good personal hygiene practice:',
        {
            'a':'Bathing daily',
            'b':'Wearing hair restraints',
            'c':'Wearing clean jewelry',
            'd':'Handwashing',
        },

    ),
    (
        'Good personal hygiene practices include:',
        {
            'a':'Not working when s ick or infectious',
            'b':'Wearing clean clothes to work',
            'c':'Trimming, cleaning, and filing fingernails frequently',
            'd':'All of the above',
        },

    ),
    (
        'Which item can be brough t into food work a reas :',
        {
            'a':'Chewing gum',
            'b':'Hair restraints',
            'c':'Lunches',
            'd':'Candy',
        },

    ),
    (
        'Personal protective equipment (PPE) in cludes:',
        {
            'a':'Gloves',
            'b':'Plastic sleeves',
            'c':'Smocks',
            'd':'All of the above',
        },

    ),
    (
        'When wearing person al protective equipment (PPE), you should:',
        {
            'a':'Modify the cut or style',
            'b':'Keep it clean a nd uncontamina ted, and change it when it becomes torn or soiled',
            'c':'Keep it on until the end of your shift, even if it is contaminated',
            'd':'None of the above',
        },

    ),
    (
        'How many steps are involved in a proper hand washing procedure:',
        {
            'a':'Seven',
            'b':'Five',
            'c':'One',
            'd':'Two',
        },

    ),
    (
        'You must always wash your hands after:',
        {
            'a':'Using the restroom for any reason',
            'b':'Touching or scratching any part of your skin, hair, eyes, or mouth',
            'c':'Eating, drinking, or smoking',
            'd':'All of the above',
        },

    ),
    (
        'Proper handwashing technique should include which of the following:',
        {
            'a':'Do not worry about cleaning under your fingernails or between fingers',
            'b':'Using the coldest water possible',
            'c':'Using the germicidal/anti-bacterial soap or sanitizer provided',
            'd':'Drying your hands on your uniform',
        },

    ),
    (
        'Where can lunches, drinks, candy, and chewing gum be allowed in food facilities:',
        {
            'a':'In processing areas',
            'b':'Only in lunchrooms, break areas, or other designated storage areas',
            'c':'In clothing storage or changing room areas',
            'd':'All of the above',
        },

    )
]

haccp = [
    (
        'HACCP stands for:',
        {
            'a':'Hazard Analysis and Critical Control Points',
            'b':'Hazards and Allergens Cause Certain Problems',
            'c':'Having any Affects Causes Control Policies',
            'd':'None of the above',
        },

    ),
    (
        'The purpose of HACCP is to:',
        {
            'a':'Make you do more work',
            'b':'Eliminate potential hazards from food to make it safe to eat',
            'c':'Clean equipmen t properly',
            'd':'None of the above',
        },

    ),
    (
        'HACCP identifies which types ofhazards:',
        {
            'a':'Biological',
            'b':'Chemical',
            'c':'Physical',
            'd':'All of the above',
        },

    ),
    (
        'Which U.S. government agencies require HACCP:',
        {
            'a':'United States Department of Agriculture',
            'b':'Food and Drug Administration',
            'c':'Both (a ) and (b)',
            'd':'Neither (a ) nor (b',
        },

    ),
    (
        'How many HACCP principles are there:',
        {
            'a':'Five',
            'b':'Three',
            'c':'Seven',
            'd':'Eight',
        },

    ),
    (
        'Which is not a principle of HACCP:',
        {
            'a':'Hazard analysis',
            'b':'HACCP team',
            'c':'Monitoring',
            'd':'Recordkeeping',
        },

    ),
    (
        'Which is an example of a physical hazard:',
        {
            'a':'Glass',
            'b':'Cleaning chemicals',
            'c':'Bacteria',
            'd':'None of the above',
        },

    ),
    (
        'Which type of hazard is the cause of food borne illness:',
        {
            'a':'Physical',
            'b':'Biological',
            'c':'Chemical',
            'd':'None of the above',
        },

    ),
    (
        'A critical control point (CCP) is:',
        {
            'a':'Identifying hazards and preventive measures',
            'b':'A point, step, or procedure in a food process at which a hazard can be controlled',
            'c':'Product sampling and testing',
            'd':'All of the above',
        },

    ),
    (
        'HACCP records must be:',
        {
            'a':'Accurate',
            'b':'Signed',
            'c':'Dated',
            'd':'All of the above',
        },

    )
]

sanitation = [
    (
        'Sanitation refers to:',
        {
            'a':'Only cleaning of equipment and food work areas',
            'b':'Only sanitizing of equipment and food work areas',
            'c':'All of the practices and procedures used to keep the facility clean and the food produced uncontaminated',
            'd':'Cleaning and sanitizing of non-food work areas',
        },

    ),
    (
        'Which of the topics are related to sanitation:',
        {
            'a':'Personal hygiene and cleanliness',
            'b':'Equipment and work area clothing',
            'c':'Pest control',
            'd':'All of the above',
        },

    ),
    (
        'Which does not require strict sanitation procedures be followed:',
        {
            'a':"Food production equipment",
            'b':"Employees' automobiles",
            'c':"Food production work areas",
            'd':"Employees' personal hygiene",
        },

    ),
    (
        'Food residue left on equipment is:',
        {
            'a':'A source of food for bacteria',
            'b':'A source of chemical contamination',
            'c':'Ok, it does not need to be cleaned off',
            'd':'All of the above',
        },

    ),
    (
        'How many steps are in a basic cleaning and sanitizing procedure:',
        {
            'a':'One',
            'b':'Two',
            'c':'Three',
            'd':'Four',
        },

    ),
    (
        'The basic steps of cleaning and sanitizing include:',
        {
            'a':'A rough clean',
            'b':'Cleaning with a chemical',
            'c':'Sanitizing',
            'd':'All of the above',
        },

    ),
    (
        'Methods of applying cleaning and sanitizing chemicals include:',
        {
            'a':'Mixing with water and apply with a brush',
            'b':'Metering and apply through a hose',
            'c':'Applying as a foam',
            'd':'All of the above',
        },

    ),
    (
        'Cleaning and sanitizing equipment and chemicals should be:',
        {
            'a':'Left any old place in the plant after use',
            'b':'Used, handled, and stored properly',
            'c':'Put away when still wet',
            'd':'None of the above',
        },

    ),
    (
        'When storing cleaning and sanitizing equipment, make sure to:',
        {
            'a':'Clean the equipment after each use',
            'b':'Dry the equipment thoroughly before putting it away',
            'c':'Store the equipment only in its designated storage area',
            'd':'All of the above',
        },

    ),
    (
        'When using cleaning and sanitizing chemicals always:',
        {
            'a':'Read and following the label instructions carefully',
            'b':'Do whatever way you want',
            'c':'Use as much or as little as you want',
            'd':'None of the above',
        },

    )
]

time =[
    (
        'The temperature "Danger Zone" is between:',
        {
            'a':'20 and 120 degrees F',
            'b':'30 and 130 degrees F',
            'c':'40 and 140 degrees F',
            'd':'50 and 150 degrees F',
        },

    ),
    (
        'Time and temperature controls are used to properly:',
        {
            'a':'Cook food',
            'b':'Cool food',
            'c':'Store food',
            'd':'All of the above',
        },

    ),
    (
        'Time and temperature controls include:',
        {
            'a':'Cooking',
            'b':'Freezing',
            'c':'Pasteurization',
            'd':'All of the above',
        },

    ),
    (
        'The purpose of time and temperature controls is to:',
        {
            'a':'Produce food faster',
            'b':'Control the growth of potentially h a rmful bacteria',
            'c':'Create a warm, moist environment',
            'd':'Make food taste good',
        },

    ),
    (
        'Which bacteria can be controlled by time and temperature:',
        {
            'a':'Listeria',
            'b':'E. coli',
            'c':'Salmonella',
            'd':'All of the above',
        },

    ),
    (
        'Which is the most commonly used time and temperature control in food processing:',
        {
            'a':'Cooking',
            'b':'Irradiation',
            'c':'Thermal processing',
            'd':'All of the above',
        },

    ),
    (
        'Cooling food to about 40 degrees Fahrenheit is called:',
        {
            'a':'Freezing',
            'b':'Pasteurizing',
            'c':'Refrigerating',
            'd':'All of the above',
        },

    ),
    (
        'The first rule to follow for time and temperature controls is:',
        {
            'a':"Being close to target is good enough",
            'b':"Always follow your company's established procedures and practices for the food you are making",
            'c':"If you make a small mistake, it won't matter much",
            'd':"None of the above",
        },

    ),
    (
        'To make sure correct time and temperature controls are met:',
        {
            'a':'Keep doors closed to coolers, freezer, holding areas, warehouses, processing rooms, any other cooled work areas',
            'b':'Never alter the specified time to heat, blanch, cook, or cool a product',
            'c':'Use a thermometer to check if a food has reached its correct processing temperature',
            'd':'All of the above',
        },

    ),
    (
        'If you think a time or temperature control may have been violated:',
        {
            'a':'Tell your supervisor or quality control person, so they can test the batch or make a decision as to what to do',
            'b':'Throw the batch away when no one is looking',
            'c':'Do not tell anyone',
            'd':'None of the above',
        },

    )
]

foreign =[
    (
        'Foreign material detection is:',
        {
            'a':'Finding objects in your morning coffee before going to work',
            'b':'Locating objects in food that should not be there',
            'c':'Sanitizing of equipment and food work areas',
            'd':'None of the above',
        },

    ),
    (
        'Foreign material detection is important because:',
        {
            'a':'It helps ensure that products does not contain foreign objects',
            'b':'It is job security for employees',
            'c':'It helps detect bacteria',
            'd':'None of the above',
        },

    ),
    (
        'Foreign materials can come from :',
        {
            'a':'Raw materials',
            'b':'Inside the plant',
            'c':'Employees',
            'd':'All of the above',
        },

    ),
    (
        'Types of foreign materials include:',
        {
            'a':'Metal',
            'b':'Glass',
            'c':'Wood',
            'd':'All of the above',
        },

    ),
    (
        'Poor personal hygiene practices are the cause of which types of contaminants:',
        {
            'a':'Chewing gum',
            'b':'Hair',
            'c':'Jewelry',
            'd':'All of the above',
        },

    ),
    (
        'It is important to conduct foreign material detection:',
        {
            'a':'When raw materials are received and when food is about to leave the plant',
            'b':'During the cooking process',
            'c':'After the food has arrived at the store',
            'd':'All of the above',
        },

    ),
    (
        'Incoming raw materials can contain which foreign materials:',
        {
            'a':'Pests',
            'b':'Dirt',
            'c':'Debris',
            'd':'All of the above',
        },

    ),
    (
        'Which equipment is used to detect foreign materials:',
        {
            'a':'A thermometer',
            'b':'Magnets and metal detectors',
            'c':'A refrigerator',
            'd':'None of the above',
        },

    ),
    (
        'Visual inspection means:',
        {
            'a':'Looking through a magnifying glass',
            'b':'Using magnets and metal detectors',
            'c':'Looking for foreign materials with the naked eye',
            'd':'None of the above',
        },

    ),
    (
        'Which control measures help prevent foreign materials from getting into food:',
        {
            'a':'Good personal hygiene practices',
            'b':'Inspection of raw materials before adding them to food',
            'c':'Good housekeeping measures',
            'd':'All of the above',
        },

    )
]

cross = [
    (
        'Cross contamination is:',
        {
            'a':'Contamination of food with crosses',
            'b':'Contamination of food with other materials',
            'c':'Contamination of food with ingredients',
            'd':'None of the above',
        },

    ),
    (
        'Which is not a possible contaminant:',
        {
            'a':'Pesticides',
            'b':'Wood',
            'c':'Bacteria',
            'd':'Moon beams',
        },

    ),
    (
        'Chemical contaminants include:',
        {
            'a':'Water',
            'b':'Cleaning chemicals',
            'c':'Milk',
            'd':'All of the above',
        },

    ),
    (
        'To prevent chemical cross contamination always:',
        {
            'a':'Store chemicals in their designated spot when not in use',
            'b':'Make sure food production areas are cleaned, rinsed, and free of chemical residue after sanitation',
            'c':'Put food and packaging materials away or cover them before cleaning or applying pesticides',
            'd':'All of the above',
        },

    ),
    (
        'Bacteria can contamina te food by hitching a ride on:',
        {
            'a':'People',
            'b':'Equipment',
            'c':'Packaging materials',
            'd':'All of the above',
        },

    ),
    (
        'To prevent bacterial cross contamination always:',
        {
            'a':'Wash your hands',
            'b':'Use footbaths and h and dipstations',
            'c':'Separate raw and cooked products',
            'd':'All ofthe a bove',
        },

    ),
    (
        'Physical hazards include:',
        {
            'a':'Metal',
            'b':'Dust',
            'c':'People',
            'd':'Water',
        },

    ),
    (
        'Horseplay includes:',
        {
            'a':'Driving a forklift recklessly',
            'b':'Using hoses to squirt co-workers',
            'c':'Throwing food',
            'd':'All of the above',
        },

    ),
    (
        'Which is not used to detect cross contamination in food:',
        {
            'a':'Metal detector',
            'b':'Screwdriver',
            'c':'Visual inspection',
            'd':'Screens and sifters',
        },

    ),
    (
        'Cross contamination occurs when:',
        {
            'a':'Rules are disobeyed',
            'b':'Control measures are inadequate',
            'c':'There is human error or accident',
            'd':'All of the above',
        },

    )
]

allergens = [
    (
        'A food allergic reaction is ca used by:',
        {
            'a':'Eating too much food',
            'b':"The body's response to a foreign protein",
            'c':'A reaction to harmful bacteria in the food',
            'd':'All of th e above',
        },

    ),
    (
        'Sufferers of food allergies commonly experience:',
        {
            'a':'Vomiting',
            'b':'Hives',
            'c':'Difficulty breathing',
            'd':'All of the above',
        },

    ),
    (
        'Common food allergen s include:',
        {
            'a':'Peanuts',
            'b':'Milk',
            'c':'Fish',
            'd':'All of the above',
        },

    ),
    (
        'The only way to treat food allergies is to:',
        {
            'a':'Get a shot',
            'b':'Lay down and rest',
            'c':'Avoid foods that trigger reactions',
            'd':'None of the above',
        },

    ),
    (
        'Food a llergens can contaminate products by improper:',
        {
            'a':'Use of ingredients',
            'b':'Use of rework',
            'c':'Clean-up or sanitation of equipment',
            'd':'All ofthe above',
        },

    ),
    (
        'To avoid accidental contamination of ingred ients with allergens:',
        {
            'a':'Check shipments of ingredients and raw materials at receiving',
            'b':'Store a llergenic ingredients separat ely from other ingredients',
            'c':'Always check the ingredients before they are added to a batch of food.',
            'd':'All of th e above',
        },

    ),
    (
        'To avoid allergen contamination when processing products, you should:',
        {
            'a':'Visually inspect equipment for allergen residue or build-up from previous production runs before processing beings on another product',
            'b':'Use separate or color-coded equipment for products that contain a known allergen',
            'c':'Ad the allergen ingredient near the end of processing',
            'd':'All of the above',
        },

    ),
    (
        'Rework that contains an allergen must be:',
        {
            'a':'Clearly labeled',
            'b':'Only used in a compatible product',
            'c':'Both (a) and (b)',
            'd':'Neither (a) nor (b)',
        },

    ),
    (
        'Proper cleanup following the processing of products that contain allergens may include:',
        {
            'a':'Disassembling equipment',
            'b':'Cleaning areas of equipment by hand',
            'c':'Visually inspecting equipment after cleaning',
            'd':'All of the above',
        },

    ),
    (
        'When working with foods that contain allergens, you should always:',
        {
            'a':'Follow all company food safety rules',
            'b':'Work as quickly as possible',
            'c':'Avoid your co-workers',
            'd':'All of the above',
        },

    )
]

pest = [
    (
        'Pests include which of the following:',
        {
            'a':'Insects',
            'b':'Birds',
            'c':'Rodents',
            'd':'All of the above',
        },

    ),
    (
        "Pest control is part of your company's:",
        {
            'a':'Sanitation program',
            'b':'Equipment maintenance',
            'c':'Microbiological testing',
            'd':'None of the above',
        },

    ),
    (
        'Pests are attracted to:',
        {
            'a':'Food',
            'b':'Water',
            'c':'Garbage',
            'd':'All of the above',
        },

    ),
    (
        'The best way to combat pests is to:',
        {
            'a':'Combat them once they arere inside the facility',
            'b':'Keep them from getting into the food facility in the first place',
            'c':'Detect them once they are in the food product',
            'd':'None of the above',
        },

    ),
    (
        'To keep pests from getting in:',
        {
            'a':'The facility s hould be tightly constructed',
            'b':'Eliminate food and water sources',
            'c':'Keep doors a nd windows shut',
            'd':'All of th e above',
        },

    ),
    (
        'Insect control methods include:',
        {
            'a':'Insecticides',
            'b':'Insect electrocutors ("zappers")',
            'c':'Heat sterilization',
            'd':'All of the above',
        },

    ),
    (
        'The methods used to apply pesticides include:',
        {
            'a':'Fogging',
            'b':'Fumigating',
            'c':'Crack-and-crevice spraying',
            'd':'All of the above',
        },

    ),
    (
        'The main method of rodent control is:',
        {
            'a':'Baiting',
            'b':'Trapping',
            'c':'Both (a) and (b)',
            'd':'Neither (a) nor (b)',
        },

    ),
    (
        'A general rule you can follow to help control rodents through baiting include:',
        {
            'a':'Using them only in designated and authorized areas',
            'b':'Inspecting and changing bait frequently',
            'c':'Disposing of, or notifying the proper person to dispose of, any rodent bodies you discover',
            'd':'All of the above',
        },

    ),
    (
        'Which is not an example of good pest control:',
        {
            'a':'Cleaning up spills',
            'b':'Leaving doors and windows open',
            'c':'Cleaning up garbage',
            'd':'Using pesticides',
        },

    )
]

security = [
    (
        'Security risks at your company can include:',
        {
            'a':'Theft',
            'b':'Assault',
            'c':'Vandalism',
            'd':'All of the above',
        },

    ),
    (
        'Parking lots can be dangerous because of:',
        {
            'a':'Unpredictable traffic patterns',
            'b':'Careless drivers',
            'c':'Hidden areas that conceal criminals',
            'd':'All of the above',
        },

    ),
    (
        'When you enter a parking lot you should park:',
        {
            'a':'Where you can clearly see around your vehicle',
            'b':'Where you can be s een',
            'c':'Close to the entrance, if possible',
            'd':'All of the above',
        },

    ),
    (
        'If there is another person in back of you who wants to enter the building, you should:',
        {
            'a':'Let them in if you know them',
            'b':'Insist that they use their own ID badge t o sca n and enter the building',
            'c':'heck their ID badge to see if th ey are the card holder, and then let them in',
            'd':'All of the above',
        },

    ),
    (
        'An area of the plant which must be kept secure is a :',
        {
            'a':'Warehouse',
            'b':'Production area',
            'c':'Laboratory',
            'd':'All of the above',
        },

    ),
    (
        'To protect product while working, you should:',
        {
            'a':'Make sure metal detectors, magnets, etc. are working properly at all times',
            'b':'Properly label product and rework',
            'c':'Report missing stock',
            'd':'All of the above',
        },

    ),
    (
        'To protect yourself while working, you should:',
        {
            'a':'Report suspicious activities',
            'b':'Report broken windows and locks',
            'c':'Be aware of your surroundings at all times',
            'd':'All of the above',
        },

    ),
    (
        'Do not bring lunch containers or purses onto the production floor because:',
        {
            'a':'There is no room for them in your work area',
            'b':'They could be used to conceal chemicals, weapons, and explosive devices',
            'c':'Other employees might take your food',
            'd':'None of the above',
        },

    ),
    (
        'Suspicious activities include:',
        {
            'a':'Acting nervous, anxious, or secretive',
            'b':'Taking pictures of work areas and equipment',
            'c':'Threatening people',
            'd':'All of the above',
        },

    ),
    (
        'Visitors at your company should:',
        {
            'a':'Register before they move about your company',
            'b':'Wear some form of identification',
            'c':'Travel with the employee they have come to see',
            'd':'All of the above',
        },

    )
]

bacteria_sp = [
                (
                    'Las bacterias son:',
                    {
                        'a':'Seres vivientes tan pequeños que solamente se los puede ver con ayuda de un microscopio',
                        'b':'Organismos vivientes lo suficientemente grandes para poderlos ver a simple vista',
                        'c':'Organismos que están hechos de "micros"',
                        'd':'Ninguna de las respuestas de arriba',
                    },

                ),

                (
                    'Las bacterias se encuentran en:',
                    {
                        'a':'Comida',
                        'b':'Tierra',
                        'c':'Intestinos de personas y animales',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Se usan bacterias para hacer:',
                    {
                        'a':'Pan',
                        'b':'Queso',
                        'c':'Salchichas de verano',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Cuál no es una bacteria nociva:',
                    {
                        'a':'Listeria',
                        'b':'E.coli',
                        'c':'Zoología',
                        'd':'Salmonela',
                    },

                ),
                (
                    'La enfermedad causada por bacteria nociva se llama:',
                    {
                        'a':'Envenenamiento microbiano',
                        'b':'Enfermedades provenientes de la comida',
                        'c':'Contaminación de la comida',
                        'd':'Infección de la comida',
                    },

                ),
                (
                    'Un síntoma común de muchas de las enfermedades provenientes de la comida incluye:',
                    {
                        'a':'Vómito',
                        'b':'Ceguera',
                        'c':'Ador mecimiento',
                        'd':'Ninguna de las respuestas de arriba',
                    },

                ),
                (
                    'Un proceso que compañías de alimentos usan para tratar de controlar las bacterias es:',
                    {
                        'a':'Refrigeración',
                        'b':'Limpieza y desinfección',
                        'c':'Cocinar',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'La práctica de higiene personal más importante para controlar la diseminación de bacterias es:',
                    {
                        'a':'Usando redes para el cabello',
                        'b':'Lavándose las manos',
                        'c':'Bañándose diariamente',
                        'd':'Ninguno de los de arriba',
                    },

                ),
                (
                    'La bacteria proveniente de deterioro puede causar que la comida se haga:',
                    {
                        'a':'Pulposa',
                        'b':'Cienosa',
                        'c':'Apestosa',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Maneras para prevenir la contaminación y controlar la bacteria en los alimentos incluyen:',
                    {
                        'a':'Controles de tiempo y temperatura',
                        'b':'higiene',
                        'c':'Control de humedad',
                        'd':'Todos los de arriba',
                    },

                ),
            ]

foodborne_sp = [
                (
                    'Las enfermedades provenientes de los alimentos afectan a cuantas personas cada año:',
                    {
                        'a':'76,000',
                        'b':'760,000',
                        'c':'76,000,000',
                        'd':'Ninguna de las respuestas de arriba',
                    },

                ),
                (
                    'Las enfermedades provenientes de los alimentos matan a cuantas personas ca da año:',
                    {
                        'a':'500',
                        'b':'5,000',
                        'c':'50,000',
                        'd':'Ninguna de las respuestas de arriba',
                    },

                ),
                (
                    'Las enfermedades provenientes de los alimentos han sido conquistadas debido a seguridad mejorada de la comida, tal como:',
                    {
                        'a':'La pasteurización de la leche',
                        'b':'Enlatado seguro',
                        'c':'Desinfección de las fuentes de agua',
                        'd':'Todas las de arriba',
                    },

                ),
                (
                    'Nuevos microorganismos surgen como problemas a la salud pública porque:',
                    {
                        'a':'Los microorganismos pueden evolucionar',
                        'b':'Nuestro entorno y la manera como estamos viviendo está cambiando',
                        'c':'Las prácticas de producción y hábitos de consumo cambian',
                        'd':'Todas las de arriba',
                    },

                ),
                (
                    'Cuando se traga microorganismos peligrosos, estos :',
                    {
                        'a':'Se quedan en los intestinos',
                        'b':'Producen una toxina',
                        'c':'Invaden tejidos profundos del cuerpo',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Los síntomas de enfermedades provenientes de los alimentos incluyen:',
                    {
                        'a':'Diarrea',
                        'b':'Retortijones estomacales',
                        'c':'Náusea',
                        'd':'Todas las de arriba',
                    },

                ),
                (
                    'La comida contaminada puede ser muy peligrosa, especialmente a:',
                    {
                        'a':'Mujeres embarazadas',
                        'b':'Niños pequeños',
                        'c':'Ancianos',
                        'd':'Todas las de arriba',
                    },

                ),
                (
                    'El tratamiento de enfermedades provenientes de los alimentos tipicamente requiere que uno:',
                    {
                        'a':'Consuma comida saludable',
                        'b':'Reciba una inyección',
                        'c':'Tome muchos líquidos',
                        'd':'Ninguna de las respuestas de arriba',
                    },

                ),
                (
                    'La comida puede volverse contaminada por:',
                    {
                        'a':'Empleados infectados',
                        'b':'Contaminación entrecruzada',
                        'c':'Ninguna ni a, ni b',
                        'd':'Ambas a, y b',
                    },

                ),
                (
                    'Se puede prevenir muchas enfermedades provenientes de los alimentos:',
                    {
                        'a':'Practicando buena higiene personal',
                        'b':'Limpiando y desinfectando equipo y áreas de trabajo',
                        'c':'Siguiendo controles de tiempo y temperatura',
                        'd':'Todas las respuestas de arriba',
                    },

                )

            ]

personalhygiene_sp = [
                (
                    'Higiene personal es:',
                    {
                        'a':'Mantenerse limpio',
                        'b':'Desinfectar el equipo y las áreas de trabajo de alimentos',
                        'c':'Llegar al trabajo a tiempo',
                        'd':'Ninguno de los de arriba',
                    },

                ),
                (
                    'Cuál no es una buena práctica de higiene personal:',
                    {
                        'a':'Bañarse diariamente',
                        'b':'Usar redes para el cabello',
                        'c':'Usar joyería limpia',
                        'd':'Lavarse las manos',
                    },

                ),
                (
                    'Las buenas prácticas de higiene personal incluyen:',
                    {
                        'a':'No trabajar cuando esté enfermo o infeccioso',
                        'b':'Usar ropa limpia en el trabajo',
                        'c':'Recortarse, limpiarse, y limarse las uñas frecuentemente',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Cuál artículo se puede traer a las áreas de trabajo de alimentos:',
                    {
                        'a':'Chicle',
                        'b':'Cubiertas o redes para el cabello',
                        'c':'Almuerzos',
                        'd':'Dulces',
                    },

                ),
                (
                    'Equipo de protección personal (PPE en inglés) incluye:',
                    {
                        'a':'Guantes',
                        'b':'Mangas plásticas',
                        'c':'Guardapolvos',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Cuando esté usando equipo de protección personal (PPE) uno debería:',
                    {
                        'a':'Modificar el corte o estilo',
                        'b':'Mantenerlo limpio y sin contaminarlo, y cambiarlo cuando se ensucie o se rasgue',
                        'c':'Mantenerlo puesto hasta el fin de la jornada aunque estuviera contaminado',
                        'd':'Ninguno de los de arriba',
                    },

                ),
                (
                    'Cuántos pasos están incluidos en el procedimiento apropiado de lavarse las manos:',
                    {
                        'a':'Siete',
                        'b':'Cinco',
                        'c':'Uno',
                        'd':'Dos',
                    },

                ),
                (
                    'Uno siempre debe lavarse las manos después de:',
                    {
                        'a':'Usar el baño por cualquier razón',
                        'b':'Tocar o rascarse cualquier parte de la piel, pelo, ojos, o boca',
                        'c':'Comer, beber, o fumar',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'La técnica apropiada de lavarse las manos debería incluir cual de las siguientes:',
                    {
                        'a':'No se preocupe acerca de limpiarse sus uñas o entre los dedos',
                        'b':'Usar la agua más fría que sea posible',
                        'c':'Usando un jabón hermicida/antibacteriano o desinfectante que ha sido suministrado',
                        'd':'Secarse las manos en su uniforme',
                    },

                ),
                (
                    'Dónde se permiten almuerzos, bebidas, dulces, o chicle de mascar en las plantas de alimento:',
                    {
                        'a':'En las áreas de proceso',
                        'b':'Solamente en los comedores, lugares de descanso, o otras áreas de almacenaje designadas',
                        'c':'En lugares donde se guarda la ropa o se cambia la ropa',
                        'd':'Todos los de arriba',
                    },

                )

            ]

haccp_sp = [
                (
                    'HACCP significa:',
                    {
                        'a':'Análisis de Peligros y Puntos Criticos de Control (HACCP en inglés)',
                        'b':'Ha Abierto Controles Con Peso',
                        'c':'Hombres Avanzan Casi Cuando Pueden',
                        'd':'Ninguno de los de arriba',
                    },

                ),
                (
                    'El propósito de HACCP es:',
                    {
                        'a':'Dar a usted más trabajo',
                        'b':'Eliminar peligros potenciales de la comida para hacerla segura de comer',
                        'c':'Limpiar el equipo apropiadamente',
                        'd':'Ninguno de los de arriba',
                    },

                ),
                (
                    'HACCP identifica qué tipo de peligro:',
                    {
                        'a':'Biológico',
                        'b':'Químico',
                        'c':'Físico',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Cuál de las agencias del gobierno de EE.DU. requiere el HACCP:',
                    {
                        'a':'El Departamento de Agricultura de Estados Unidos',
                        'b':'La Administración de Alimentos y Drogas',
                        'c':'Ambos (a ) y (b)',
                        'd':'Ni (a) ni (b )',
                    },

                ),
                (
                    'Cuántos principios de HACCP hay:',
                    {
                        'a':'Cinco',
                        'b':'Tres',
                        'c':'Siete',
                        'd':'Ocho',
                    },

                ),
                (
                    'Cuál no es un principio de HACCP:',
                    {
                        'a':'Análisis de Peligros',
                        'b':'Equipo HACCP',
                        'c':'Monitoreo',
                        'd':'Mantenimiento de archivos',
                    },

                ),
                (
                    'Cuál es un ejemplo de un peligro físico:',
                    {
                        'a':'Vidrio',
                        'b':'Químicos de limpieza',
                        'c':'Bacterias',
                        'd':'Ninguno de los de arriba',
                    },

                ),
                (
                    'Cuál tipo de peligro es la causa de enfermedades provenientes de la comida:',
                    {
                        'a':'Físico',
                        'b':'Biológico',
                        'c':'Químico',
                        'd':'Ninguno de los de arriba',
                    },

                ),
                (
                    'Un punto de control crítico (CCP) es:',
                    {
                        'a':'Identificando los peligros y medidas de prevención',
                        'b':'Un punto, paso, o procedimiento en el proceso de alimentos donde se puede controlar un peligro',
                        'c':'Muestras y pruebas del producto',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Los archivos o registros de HACCP deben ser:',
                    {
                        'a':'Precisos',
                        'b':'Firmados',
                        'c':'Fechados',
                        'd':'Todos los de arriba',
                    },

                )

            ]

sanitation_sp = [
                (
                    'Saneamiento se refiere a:',
                    {
                        'a':'Solamente la limpieza del equipo y las áreas de producción de alimentos',
                        'b':'Solamente la desinfección del equipo y las áreas de trabajo con alimentos',
                        'c':'Todas las prácticas de procedimientos que se usan para mantener al lugar limpio y la comida producida sin contaminación',
                        'd':'Limpieza y desinfección de las áreas de trabajo donde no hay alimentos',
                    },

                ),
                (
                    'Cuál de los tópicos está relacionado a saneamiento:',
                    {
                        'a':'Higiene y limpieza personal',
                        'b':'Equipo y la ropa que se usa en el lugar de trabajo',
                        'c':'Control de plagas',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Cuál no requiere que se sigan procedimientos de saneamiento estrictos:',
                    {
                        'a':'Equipo de producción de alimentos',
                        'b':'Automóviles de los empleados',
                        'c':'Producción de alimentos en las áreas de trabajo',
                        'd':'La higiene personal de los empleados',
                    },

                ),
                (
                    'El residuo de la comida que queda en el equipo es:',
                    {
                        'a':'Una fuente de alimento para las bacterias',
                        'b':'Una fuente de contaminación quimica',
                        'c':'No importa, no necesita ser limpiado',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Cuántos pasos existen en el procedimiento basico de limpieza y desinfección:',
                    {
                        'a':'Uno',
                        'b':'Dos',
                        'c':'Tres',
                        'd':'Cuatro',
                    },

                ),
                (
                    'Los pasos básicos de limpieza y desinfección incluyen:',
                    {
                        'a':'Limpieza inicial',
                        'b':'Limpieza con un quimico',
                        'c':'Desinfección',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Los metodos para aplicar químicos de limpieza y desinfección incluyen:',
                    {
                        'a':'Mezclarlos con agua y aplicarlos con un cepillo',
                        'b':'Medir y aplicarlo por medio de una manguera',
                        'c':'Aplicarlos como una espuma',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'El equipo de limpieza e higiene y los químicos deben ser:',
                    {
                        'a':'Puestos donde quiera en la planta después de usarlos',
                        'b':'Usarlos, manejarlos, y almacenarlos apropiadamente',
                        'c':'Guardarlos cuando todavía esten mojados',
                        'd':'Ninguno de los de arriba',
                    },

                ),
                (
                    'Cuando esté almacenando equipo de limpieza y desinfección, asegúrese que:',
                    {
                        'a':'Limpie el equipo después de cada uso',
                        'b':'Seque el equipo completamente antes de guardarlo',
                        'c':'Almacene el equipo sólo en un área de almacenaje designada',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Cuando use químicos de limpieza y desinfección siempre:',
                    {
                        'a':'Lea y siga con cuidado las instrucciones de la etiqueta',
                        'b':'Hágalo de cualquier manera que usted lo desee',
                        'c':'Use tan poco o mucho silo desea',
                        'd':'Ninguno de los de arriba',
                    },

                )

            ]

time_sp = [
                (
                    'La temperatura de "zona de peligro" está entre:',
                    {
                        'a':'20 y 120 °F',
                        'b':'30 y 130 °F',
                        'c':'40y140 °F',
                        'd':'50 y 150 °F',
                    },

                ),
                (
                    'Los controles de tiempo y temperatura se usan para apropiadamente:',
                    {
                        'a':'Cocinar comida',
                        'b':'Enfriar comida',
                        'c':'Almacenar comida',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Los controles de tiempo y temperatura incluyen :',
                    {
                        'a':'Cocinar',
                        'b':'Congelar',
                        'c':'Pasteurizar',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'El propósito de los controles de tiempo y temperatura es para:',
                    {
                        'a':'Producir la comida más rápidamente',
                        'b':'Controlar el crecimiento de bacterias potencialmente peligrosas',
                        'c':'Crear un entorno caliente, húmedo',
                        'd':'Hacer que la comida sepa bien',
                    },

                ),
                (
                    'Cuál de las bacterias pueden controlarse por tiempo y temperatura:',
                    {
                        'a':'Listeria',
                        'b':'E. coli',
                        'c':'Salmonela',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Cuál es el control de tiempo y temperatura que se usa más comúnmente en el procesamiento de comida:',
                    {
                        'a':'Cocinar',
                        'b':'Irradiar',
                        'c':'Procesar térmicamente',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Enfriando los alimentos cerca a 40 grados Fahrenheit se llama:',
                    {
                        'a':'Congelar',
                        'b':'Pasteurizar',
                        'c':'Refrigerar',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'La primera regla a seguirse en los controles de tiempo y temperatura es:',
                    {
                        'a':'Estar cerca del punto, es suficiente',
                        'b':'Siempre siga los procedimientos y prácticas establecidos en su companía para los alimentos que está elaborando',
                        'c':'Si hace un pequeño error, no importa mayormente',
                        'd':'Ninguno de los de arriba',
                    },

                ),
                (
                    'Para asegurarse que se ha conformado a los controles correctos de tiempo y temperatura:',
                    {
                        'a':'Mantenga las puertas cerradas para refrigeradoras, congeladoras, lugares de sostén, depósitos, recintos de proceso, y otras áreas de trabajo enfriadas',
                        'b':'Nunca altere el tiempo especificado para calentar, blanquear, cocinar, o enfriar un producto',
                        'c':'Use un termómetro para verificar si la comida ha llegado a su temperatura de proceso correcta',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Si usted piensa que se ha violado un control de tiempo y temperatura:',
                    {
                        'a':'Digale a su supervisor o persona de control de calidad, de manera que pueda comprobar un lote o hacer una decision en lo que debería seguirse',
                        'b':'Deseche el lote cuando nadie esté mirando',
                        'c':'No le diga a nadie',
                        'd':'Ninguno de los de arriba',
                    },

                )

            ]

foreign_sp = [
                (
                    'La detección de materia foránea es:',
                    {
                        'a':'Encontrar objetos en su café mañanero antes de ir a trabajar',
                        'b':'Localizar objetos en la comida que no deberían estar ahí',
                        'c':'Desinfectar el equipo y áreas de! trabajo de alimentos',
                        'd':'Ninguno de las de arriba',
                    },

                ),
                (
                    'La detección de materia foránea es importante porque:',
                    {
                        'a':'Ayuda a garantizar que los productos no contengan objetos extraños',
                        'b':'Es la seguridad de trabajo para los empleados',
                        'c':'Ayuda a detectar bacterias',
                        'd':'Ninguno de los de arriba',
                    },

                ),
                (
                    'La materia foránea puede venir de:',
                    {
                        'a':'Materia prima',
                        'b':'Dentro de la planta',
                        'c':'Empleados',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Los tipos de materias foráneas incluyen:',
                    {
                        'a':'Metal',
                        'b':'Vidrio',
                        'c':'Madera',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Prácticas de higiene personal incorrectas son la causa de cuáles tipos de contaminantes:',
                    {
                        'a':'Chicle',
                        'b':'Pelo',
                        'c':'Joyería',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Es importante conducir detección de materias foráneas:',
                    {
                        'a':'Cuando se recibe la materia prima y cuando la comida está poco antes de salir de la planta',
                        'b':'Durante el proceso de cocinarla',
                        'c':'Después de que la comida ha llegado a la tienda',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Materia prima que entra puede contener materia foráneas:',
                    {
                        'a':'Plagas',
                        'b':'Tierra',
                        'c':'Basura',
                        'd':'Todos los de arriba'
                    },

                ),
                (
                    'Cuál equipo se usa para detectar materia foráneas:',
                    {
                        'a':'Un termometro',
                        'b':'Imanes y detectores de metal',
                        'c':'Un refrigerador',
                        'd':'Ninguno de los arriba',
                    },

                ),
                (
                    'Las inspeccion visual significa:',
                    {
                        'a':'Mirando a traves de un lente de aumento',
                        'b':'Usando imanes y detectores de metal',
                        'c':'Buscando materias foráneas a ojo pelado',
                        'd':'Ninguno de los de arriba',
                    },

                ),
                (
                    'Cuál medida de control ayuda a evitar que las materias foráneas se metan a la comida:',
                    {
                        'a':'Buenas prácticas de higiene personal',
                        'b':'Inspeccion de materia prima antes de añadirla a la comida',
                        'c':'Medidas de buen orden en sitio',
                        'd':'Todos los de arriba'
                    },

                )

            ]

cross_sp = [
                (
                    'La contaminación entrecruzada es:',
                    {
                        'a':'Contaminación de la comida con cruces',
                        'b':'Contaminación de comida con otros materiales',
                        'c':'Contaminación de comida con ingredientes',
                        'd':'Ninguna de las respuestas de arriba',
                    },

                ),
                (
                    'Cuál no puede ser un contaminante posible:',
                    {
                        'a':'Pesticidas',
                        'b':'Madera',
                        'c':'Bacteria',
                        'd':'Rayos de luna',
                    },

                ),
                (
                    'Contaminantes químicos incluyen:',
                    {
                        'a':'Agua',
                        'b':'Químicos de limpieza',
                        'c':'Leche',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Para evitar la contaminación entrecruzada siempre :',
                    {
                        'a':'Almacene los quimicos en su lugar designado cuando no se usen',
                        'b':'Garantice que las áreas de producción de alimentos esten limpias, bien enjaguadas, y libres de residuo quimico después de desinfección',
                        'c':'Ponga comida y materiales de empaque lejos o cúbralos antes de limpiar o aplicar pesticidas',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Las bacterias pueden contaminar los alimentos dándose un aventón en:',
                    {
                        'a':'Gente',
                        'b':'Equipo',
                        'c':'Materiales de empaque',
                        'd':'Todos los de a rriba',
                    },

                ),
                (
                    'Para impedir la contaminación entrecruzada bacteriana siempre:',
                    {
                        'a':'Lávese las manos',
                        'b':'Use lavados de pies y estaciones para desinfectar las manos',
                        'c':'Separe los productos crudos y cocinados',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Peligros físicos incluyen:',
                    {
                        'a':'Metal',
                        'b':'Polvo',
                        'c':'Personas',
                        'd':'Agua',
                    },

                ),
                (
                    'Payasadas incluyen:',
                    {
                        'a':'Manejo de un montacargas imprudentemente',
                        'b':'Usando mangueras para mojar los compañeros',
                        'c':'Tirar comida',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Qué no se usa para detector la contaminación entrecruzada en la comida:',
                    {
                        'a':'Un detector de metal',
                        'b':'Un destornillador',
                        'c':'Una inspección visual',
                        'd':'Mallas y escudriñadores',
                    },

                ),
                (
                    'La contaminación entrecruzada ocurre cuando:',
                    {
                        'a':'No se obedecen las reglas',
                        'b':'Las medidas de control son inadecuadas',
                        'c':'Hay un error o accidente humano',
                        'd':'Todos los de arriba',
                    },

                )

            ]

allergens_sp = [
                (
                    'Una reacción alérgica a los alimentos es causada por:',
                    {
                        'a':'Comer demasiada comida',
                        'b':'La reacción del cuerpo a una proteína foránea',
                        'c':'Una reacción a bacterias peligrosas en la comida',
                        'd':'Todo lo de arriba',
                    },

                ),
                (
                    'Las personas que tienen alérgias generalmente sufren de:',
                    {
                        'a':'Vómito',
                        'b':'Urticaria',
                        'c':'Dificultad en respirar',
                        'd':'Todo lo de arriba',
                    },

                ),
                (
                    'Alérgenos alimenticios comunes incluyen:',
                    {
                        'a':'Cacahuates (maní)',
                        'b':'Leche',
                        'c':'Pescado',
                        'd':'Todo lo de arriba',
                    },

                ),
                (
                    'La única manera de dar tratamiento a los alérgenos alimenticios es:',
                    {
                        'a':'Recibir una inyección',
                        'b':'Recostar se y descansar',
                        'c':'Evitar comidas que ca usen la reacción alérgica',
                        'd':'Ninguna de las respuestas de arriba',
                    },

                ),
                (
                    'Los alérgenos de los alimentos pueden contaminar los productos por:',
                    {
                        'a':'uso inapropiado de los ingredientes',
                        'b':'utilización de ingredientes usados anteriormente (reprocesados)',
                        'c':'limpieza o higiene inapropiada del equipo',
                        'd':'Todo lo de arriba',
                    },

                ),
                (
                    'Para evitar contaminación accidental de ingredientes con alérgenos:',
                    {
                        'a':'Chequee embarques de ingredientes y materia prima recibidos',
                        'b':'Almacene ingredientes alérgenicos separándolos de otros ingredientes',
                        'c':'Siempre chequee los ingredientes antes de que se los añada a un lote de alimentos.',
                        'd':'Todo lo de arriba',
                    },

                ),
                (
                    'Para evitar la contaminación de alérgenos cuando se procesen productos, uno debería:',
                    {
                        'a':'Inspeccionar visualmente el equipo para determinar que no haya residuo o acumulación de alérgenos provenientes de producciones anteriores, antes de comenzar a procesar otro producto.',
                        'b':'Usar equipo separado, o codificado a color, para productos que contengan un alérgeno conocido',
                        'c':'Añadir el ingrediente alérgeno cerca del fin del proceso',
                        'd':'Todo lo de arriba',
                    },

                ),
                (
                    'El reproceso que contengan alérgenos usados anteriormente se debe:',
                    {
                        'a':'Etiquetar así con claridad',
                        'b':'Utilizar sólo en productos compatibles',
                        'c':'Ambas a. y b.',
                        'd':'Ni a, nib.',
                    },

                ),
                (
                    'La limpieza apropiada que sigue al procesamiento de productos que contengan alérgenos quizas puede incluir:',
                    {
                        'a':'Desarmar el equipo',
                        'b':'Limpiar lugares y partes del equipo a mano',
                        'c':'Visualmente inspeccionar el equipo después de limpiarlo',
                        'd':'Todo lo de arriba',
                    },

                ),
                (
                    'Cuando se trabaja con comidas que contiene alérgenos, uno siempre debería:',
                    {
                        'a':'Seguir todas las reglas de seguridad de la compañía',
                        'b':'Trabajar lo más rapidamente posible',
                        'c':'Evitar contacto con los compañeros',
                        'd':'Todo lo de arriba',
                    },

                )

            ]

pest_sp = [
                (
                    'Las plagas incluyen cuáles de las siguientes:',
                    {
                        'a':'Insectos',
                        'b':'Pájaros',
                        'c':'Roedores',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'El control de plagas es parte de cuál programa de su compania:',
                    {
                        'a':'Programa de higiene',
                        'b':'Mantenimiento del equipo',
                        'c':'Pruebas microbiológicas',
                        'd':'Ninguno de los e arriba',
                    },

                ),
                (
                    'A las plagas les atrae:',
                    {
                        'a':'Comida',
                        'b':'Agua',
                        'c':'Basura',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'La mejor manera de combatir plagas es:',
                    {
                        'a':'Combatirlas una vez que estén dentro de la planta',
                        'b':'Mantenerlas fuera de la planta de alimentos desde un principio',
                        'c':'Detectarlas una vez que estén en el producto comestible',
                        'd':'Ninguno de los de arriba',
                    },

                ),
                (
                    'Para mantener las plagas afuera:',
                    {
                        'a':'La planta tiene que estar bien sellada',
                        'b':'Eliminar fuentes de comida y agua',
                        'c':'Mantener las puertas y ventanas cerradas',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Los métodos de control de insectos incluye:',
                    {
                        'a':'Insecticidas',
                        'b':'Aparatos para electrocutar insectos ("zappers")',
                        'c':'Esterilización por medio de calor',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Los métodos que se usan para aplicar pesticidas incluye:',
                    {
                        'a':'Hacer neblina con químicos',
                        'b':'Fumigación',
                        'c':'Rocío de grietas y hendeduras',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'El método principal de control de plagas es:',
                    {
                        'a':'Cebar',
                        'b':'Atrapar',
                        'c':'Ambas (a) y (b)',
                        'd':'Ninguno, ni (a) ni (b)',
                    },

                ),
                (
                    'Una regla general que usted puede seguir para apoyar el control de roedores por medio de cebar incluye:',
                    {
                        'a':'Usándolo solamente en áreas designadas y autorizadas',
                        'b':'Inspeccionando y cambiando los cebos frecuentemente',
                        'c':'Disponiendo, o notificando a la persona apropiada que deseche cualquier cuerpo de roedor que se encuentre',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Cuál no es un ejemplo de un buen control de plagas:',
                    {
                        'a':'Limpieza de los derrames',
                        'b':'Dejando las puertas y ventanas abiertas',
                        'c':'Limpieza de basura',
                        'd':'Usando pesticidas',
                    },

                )

            ]

security_sp =[
                (
                    'Los riesgos de seguridad en su compania puede incluir:',
                    {
                        'a':'Robo',
                        'b':'Asalto',
                        'c':'Vandalismo',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Los parques de estacionamiento pueden ser peligrosos porque:',
                    {
                        'a':'Hay patrones de trafico que no se pueden anticipar',
                        'b':'Choferes descuidados',
                        'c':'Lugares escondidos que pueden encubrir a criminales',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Cuando entra en un parque de estacionamiento, usted debería estacionarse:',
                    {
                        'a':'Donde puede ver claramente alrededor de su vehículo',
                        'b':'Donde le pueda ser visto',
                        'c':'Cerca de la entrada, si es posible',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Si hay otra persona detrás suyo que desea entrar al edificio, usted debería:',
                    {
                        'a':'Dejarles entrar si los conoce',
                        'b':'Insistir que usen su propia placa de identificación para que lo escanean para entrar al edificio',
                        'c':'Verificar sus placas de identificación para ver que sea el dueño de la placa, y luego permitirle entrar',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Un lugar en la planta que debe mantenerse segura es:',
                    {
                        'a':'Almacén',
                        'b':'Área de producción',
                        'c':'Laboratorio',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Para proteger el producto mientras trabaja, usted debería:',
                    {
                        'a':'Asegurarse que los detectores de metal, imanes, etc. estén funcionando apropiadamente.',
                        'b':'Apropiadamente etiquetar y el producto que se reprosesa',
                        'c':'Reportar cualquier existencia faltante',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Para protegerse mientras trabaje, usted debería:',
                    {
                        'a':'Reportar actividades sospechosas',
                        'b':'Reportar ventanas y candados rotos',
                        'c':'Estar consciente de todo a su alrededor todo el tiempo',
                        'd':'Todo lo de arriba',
                    },

                ),
                (
                    'No traiga contenedor de almuerzo o bolsas dentro de producción porque:',
                    {
                        'a':'No hay espacio para estos en su lugar de trabajo',
                        'b':'Estos podrian usarse para esconder químicos, armas, y aparatos explosivos',
                        'c':'Otros empleados pueden adueñarse de su comida',
                        'd':'Ninguno de los de arriba',
                    },

                ),
                (
                    'Actividades sospechosas incluyen:',
                    {
                        'a':'Actitud nerviosa, angustiada, o sigilosa',
                        'b':'Tomar fotos de las áreas y equipo de trabajo',
                        'c':'Actitud amenazante a las personas',
                        'd':'Todos los de arriba',
                    },

                ),
                (
                    'Visitantes a su compania deberían:',
                    {
                        'a':'Registrarse antes de que entren y caminen dentro de su compania',
                        'b':'Llevar puesta alguna forma de identificación',
                        'c':'Caminar con el empleado a quien han venido a visitar',
                        'd':'Todos los de arriba',
                    },

                )

            ]

fltc = [
        (
            'Forklift inspections are only required once per year.',
            OrderedDict([('True' ,'True',),('False','False')]),

        ),
        (
            'A forklift will tip over if the center of gravity is outside the stability triangle.',
            OrderedDict([('True' ,'True',),('False','False')]),

        ),
        (
            'OSHA requires retraining at least every 3 years.',
            OrderedDict([('True' ,'True',),('False','False')]),

        ),
        (
            'The safest way to cross a railroad track is at an angle.',
            OrderedDict([('True' ,'True',),('False','False')]),

        ),
        (
            'If the forklift does not have a seatbelt then it is not required on that particular model.',
            OrderedDict([('True' ,'True',),('False','False')]),

        ),
        (
            'Forklifts are designed to handle loads of any size and weight.',
            OrderedDict([('True' ,'True',),('False','False')]),

        ),
        (
            'Driving with an obstructed view is allowed if it is only within 10 yards.',
            OrderedDict([('True' ,'True',),('False','False')]),

        ),
        (
            'Although forklift injuries are common, no one has ever been killed in a forklift accident.',
            OrderedDict([('True' ,'True',),('False','False')]),

        ),
        (
            'Maximum safe speed should be equivalent to around 20 miles per hour.',
            OrderedDict([('True' ,'True',),('False','False')]),

        ),
        (
            'It is okay to give someone in management a ride if the walk is more than 200 yards.',
            OrderedDict([('True' ,'True',),('False','False')]),

        ),
        (
            'No person is allowed to pass underneath a raised load.',
            OrderedDict([('True' ,'True',),('False','False')]),
            '11'
        ),
        (
            'If the load is too heavy or too far from the fulcrum the forklift will tip forward.',
            OrderedDict([('True' ,'True',),('False','False')]),
            '12'
        ),
        (
            'The “Load Center” is the sensor on the forklift that warns if the load is too heavy.',
            OrderedDict([('True' ,'True',),('False','False')]),
            '13'
        ),
        (
            'Without a load a forklift can never tip over.',
            OrderedDict([('True' ,'True',),('False','False')]),
            '14'
        ),
        (
            'If a forklift begins to tip over you should quickly jump away from the forklift and falling items.',
            OrderedDict([('True' ,'True',),('False','False')]),
            '15'
        ),
        (
            'Driving across a slope or angle could cause the forklift to tip over.',
            OrderedDict([('True' ,'True',),('False','False')]),
            '16'
        ),
        (
            'When transporting a load on a slope, always keep the forks pointed downhill.',
            OrderedDict([('True' ,'True',),('False','False')]),
            '17'
        ),
        (
            'Forks should be lowered to the ground when the operator is more than 25 feet away.',
            OrderedDict([('True' ,'True',),('False','False')]),
            '18'
        ),
        (
            'Battery charging should only be done in designated areas.',
            OrderedDict([('True' ,'True',),('False','False')]),
            '19'
        ),
        (
            'Lifting an employee on the forks is approved only if your supervisor is watching',
            OrderedDict([('True' ,'True',),('False','False')]),
            '20'
        )
    ]

fltc_sp = [
        (
            'El montacargas requiere inspección sólo una vez al año.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),

        ),
        (
            'Un montacargas se volcará si el centro de gravedad está fuera del triángulo de estabilidad.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),

        ),
        (
            'OSHA exige volver a capacitarse al menos cada tres años.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),

        ),
        (
            'La manera más segura de cruzar rieles ferroviarios es en ángulo.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),

        ),
        (
            'Si el montacargas no tiene cinturón de seguridad es porque no necesita ese modelo en particular.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),

        ),
        (
            'Los montacargas están diseñados para maniobrar cargas de cualquier tamaño y peso.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),

        ),
        (
            'Se permite conducir con obstrucción visual sólo si es una distancia corta.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),

        ),
        (
            'Aunque las lesiones con montacargas son comunes, nadie ha muerto nunca en un accidente de montacargas.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),

        ),
        (
            'La velocidad máxima segura equivaldría alrededor de 20 millas por hora.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),

        ),
        (
            'Está bien llevar a un administrador como pasajero si el recorrido es mayor de 200 yardas.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),

        ),
        (
            'No se permite a nadie pasar por debajo de una carga levantada.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),
            '11'
        ),
        (
            'Si la carga es demasiado pesada o está muy lejos del punto de apoyo el montacargas se inclinará hacia delante.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),
            '12'
        ),
        (
            'El “centro de carga” es un detector del montacargas que le advierte si la carga es demasiado pesada.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),
            '13'
        ),
        (
            'Sin carga un montacargas nunca puede volcarse.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),
            '14'
        ),
        (
            'Si un montacargas empieza a volcarse usted debe rápidamente saltar fuera del montacargas y de los objetos que caen.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),
            '15'
        ),
        (
            'Manejar a través de una pendiente o en ángulo puede ocasionar un vuelco del montacargas.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),
            '16'
        ),
        (
            'Cuando transporte una carga por una pendiente, mantenga siempre las horquillas apuntando cuesta abajo.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),
            '17'
        ),
        (
            'Las horquillas deben bajarse al suelo cuando el operador se aleja a más de 25 pies.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),
            '18'
        ),
        (
            'La carga de la batería debe hacerse sólo en áreas designadas.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),
            '19'
        ),
        (
            'Levantar a un empleado en el montacargas está aprobado sólo si su supervisor está vigilando.',
            OrderedDict([('True' ,'Verdad',),('False','Falso')]),
            '20'
        )
    ]

wps = [
        (
            'One aspect of proper lifting techniques means that you:',
            {
                'a':'Hold the load as far from your body as possible',
                'b':'Get help with larger loads',
                'c':'Bend your back and keep your knees straight',
                'd':'Twist your back slowly if you need to turn while lifting',
            },

        ),
        (
            'Housekeeping is essential to a safe workplace because:',
            {
                'a':'It shows you take pride in your work',
                'b':'It makes your job easier',
                'c':'It saves your company money',
                'd':'Clutter and improperly stored materials are a safety and fire hazard',
            },

        ),
        (
            'Lockout/tagout devices must be attached by:',
            {
                'a':'The machine operator',
                'b':'The authorized employee or his helper',
                'c':'The authorized employee',
                'd':'The machine operator or a supervisor',
            },

        ),
        (
            'Your company must have a safety data sheet (or SDS) for each chemical that poses a physical or health hazard at your workplace.',
            OrderedDict([('True' ,'True',),('False','False')]),

        ),
        (
            'Protecting an extension cord while you work helps prevent damage that can cause electric shock.  This includes:',
            {
                'a':'Stapling the cord to secure it in place',
                'b':'Leaving slack in the cord when you use the tool',
                'c':'Running the cord under carpet to protect it from foot traffic',
                'd':'All of the above',
            },

        ),
        (
            'The best defense against a fire is to:',
            {
                'a':'Know how to use a fire extinguisher',
                'b':'Know the different classes of fire extinguishers',
                'c':'Know how to prevent fires in the first place',
                'd':'Know where your headcount area is located',
            },

        ),
        (
            'When a pedestrian encounters a forklift, the right-of-way goes to:',
            {
                'a':'The forklift',
                'b':'The forklift, if it gets to the intersection first',
                'c':'The forklift, if it’s approaching from the right',
                'd':'The pedestrian',
            },

        ),
        (
            'If a power tool has a safety guard, you must:',
            {
                'a':'Remove the guard just before using the tool',
                'b':'Never remove the safety guard when using the tool',
                'c':'Contact the tool manufacturer to see if the guard is really necessary',
                'd':'Carry the tool by the cord or hose',
            },

        ),
        (
            'When climbing a ladder, you should:',
            {
                'a':'Face the ladder',
                'b':'Use one hand to grasp the ladder',
                'c':'Carry any object or load, as long as it doesn’t affect your balance',
                'd':'All of the above',
            },

        ),
        (
            'Universal precautions are:',
            {
                'a':'A method of selecting appropriate PPE when a bloodborne pathogen incident occurs',
                'b':'A system of seven steps to follow when cleaning up machinery following an incident',
                'c':'An approach to infection control that considers all blood and body fluids to be infectious',
                'd':'None of the above',
            },

        )

    ]

wps2 = [
        (
            '_________________ responsible for providing you with a safe workplace.',
            {
                'a':'OSHA is',
                'b':'Your employer is',
                'c':'Your co-workers are',
                'd':'You are',
            },
            '11'
        ),
        (
            '_______________ ultimately responsible for my personal safety.',
            {
                'a':'I am',
                'b':'My employer is',
                'c':'OSHA is',
                'd':'My co-workers are',
            },
            '12'
        ),
        (
            'Ergonomics is a method of:',
            {
                'a':'Achieving higher productivity',
                'b':'Making the workstation and work fit your body',
                'c':'Reaching a team consensus',
                'd':'Calculating workers’ compensation costs',
            },
            '13'
        ),
        (
            'Simple movements can cause injuries if they are repeated enough.',
            OrderedDict([('True' ,'True',),('False','False')]),
            '14'
        ),
        (
            'When planning your route before you lift, you should make sure:',
            {
                'a':'You have a map of the route you’re taking',
                'b':'Your path is clear of slipping and tripping hazards',
                'c':'You put on proper PPE',
                'd':'The load meets OSHA requirements',
            },
            '15'
        ),
        (
            'You can size up a load before you lift it by:',
            {
                'a':'Carrying the load to a scale and weighing it',
                'b':'Asking someone else if they think it’s too heavy for you to lift',
                'c':'Testing the weight by moving one of the corners',
                'd':'None of the above',
            },
            '16'
        ),
        (
            'Which of the following is a proper lifting technique to use:',
            {
                'a':'Bend at the waist',
                'b':'Carry the load away from your body',
                'c':'Bend at the knees',
                'd':'Lift slowly and let your back do the work',
            },
            '17'
        ),
        (
            'Proper housekeeping procedures include:',
            {
                'a':'Clean up spills right away',
                'b':'Clean up grease and oil immediately',
                'c':'Remove ice and snow',
                'd':'All of the above',
            },
            '18'
        ),
        (
            'Good housekeeping prevents accidents and injuries because it:',
            {
                'a':'Creates a pleasant work environment',
                'b':'Keeps work areas free of materials and obstructions that can cause hazards',
                'c':'Provides exercise by bending over to pick up debris',
                'd':'Presents a good company image',
            },
            '19'
        ),
        (
            'Lockout is required:',
            {
                'a':'During servicing and maintenance where unexpected start up of equipment could harm employees',
                'b':'During repair, renovation and replacement work',
                'c':'During modifications and adjustments to powered equipment',
                'd':'All of the above',
            },
            '20'
        ),
        (
            'Lockout/Tagout is required when you:',
            {
                'a':'Stop the machine at the end of a normal shift',
                'b':'Unplug a drill to change a drill bit',
                'c':'Remove a machine guard to clear a jam',
                'd':'None of the above',
            },
            '21'
        )
    ]
