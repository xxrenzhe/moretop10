#!/usr/bin/env python3
"""Rewrite category landing + comparison FAQs to niche buyer Q&A.

Live snapshots reused a robot-vac dock/mop FAQ (and generic chart/meta FAQs)
on every money page. This module:

  - keeps the automated-dock Q&A on robot-vacuums only
  - replaces landing + comparison FAQ blocks with 3–5 intent-led Q&As
    grounded in that category's existing pick / skip / description copy
  - drops commission / score-formula / “how many we rank” / price-live meta FAQs
  - buyer-intent Q&As only (page-type FAQ规范 lives in a separate docs PR)
  - rebuilds FAQPage JSON-LD from the visible Q&As

Bake-only — not a Live deploy. No new product claims.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

KEEP_ROBOT_VAC_SLUGS = frozenset({"robot-vacuums"})

DOCK_Q = "Do I need the most automated dock?"
DOCK_A = (
    "Only if you mop often or hate emptying a bin. Many homes are happier with a "
    "mid-chart pick that self-empties dry debris and keeps mopping optional."
)
DOCK_PHRASES = ("most automated dock", "mop often", "mopping optional")

# Chart / methodology / price-live copy belongs in disclosure or the FAQ规范
# docs PR — not this buyer-intent surface.
META_FAQ_PHRASES = (
    "how many products do you rank",
    "how do you rank products",
    "do you earn a commission",
    "do you sell these products",
    "what do the scores mean",
    "how often do rankings change",
    "how often do prices change",
    "are these prices live",
    "are moretop10 prices live",
    "what if the #1 is out of stock",
    "what if chart #1 is out of stock",
)

# Buyer Q&As only — 3–5 niche questions per category. No meta/commission/price FAQ.
# Copy is restated from landing descriptions, pick taglines, and skip notes.
CATEGORY_FAQS: dict[str, list[tuple[str, str]]] = {
    "robot-vacuums": [
        (DOCK_Q, DOCK_A),
        (
            "Do I need obstacle avoidance for pets and chair legs?",
            "Yes if you have chair legs, thresholds, or pets that leave toys on the floor. "
            "Confirm carpet type and pet size on the retailer page before you buy.",
        ),
        (
            "Is a self-empty dock enough, or do I need mop wash and dry?",
            "A mid-range home often wants one dock that empties dust and washes and dries mop pads. "
            "Skip hot-water dock washing or HydroJet roller mopping if you do not mop hard.",
        ),
        (
            "When should I skip the flagship robot mop?",
            "Skip if you want deep-carpet dual-brush mopping, you are under a mid-chart budget, "
            "or you do not need auto mop wash and dry at the dock. Confirm mop pads, bags, and "
            "dock footprint on the retailer page.",
        ),
    ],
    "wet-dry-vacuums": [
        (
            "Can a wet-dry vacuum mop thick carpet?",
            "No. These cordless vacuum-mop combos are for sealed hard floors—laminate, vinyl plank, "
            "and tile. Skip if you mainly have thick carpet.",
        ),
        (
            "Do I need a self-cleaning roller?",
            "Self-clean and high-temp drying help after everyday spill cleanup so you are not "
            "rinsing a mop bucket. Confirm steam option, hard-floor fit, and tank emptying on "
            "the retailer page.",
        ),
        (
            "Do I still have to empty the dirty-water tank?",
            "Yes. Heated drying does not remove the need to empty the dirty-water tank after use. "
            "Leaving wet sludge in the collection bin will cause odors regardless of roller drying.",
        ),
        (
            "When should I pick a wet-dry stick instead of a robot mop?",
            "Choose a wet-dry combo for spill cleanup and sealed-floor mopping you want to do "
            "yourself. Skip it if you rarely mop—a stick vac alone may be enough—and skip steam "
            "models if you do not need steam.",
        ),
    ],
    "standing-desks": [
        (
            "What height range should I look for on an electric standing desk?",
            "Chart desks commonly adjust from about 28.3\" to 46.5\" with memory presets for "
            "sit-stand habits. Confirm the listed height range on the retailer page for your height.",
        ),
        (
            "How stable are these sit-stand desks?",
            "Listings call out reinforced steel frames, dual crossbeams, and load ratings around "
            "176 lbs on several FEZIBO sizes. Confirm the weight rating if you run dual monitors "
            "or a PC tower.",
        ),
        (
            "What size standing desk do I need for a home office?",
            "48×24 is Best value for apartments and narrow alcoves. 60×30 with drawers is the "
            "daily home-office pick. Skip 83-inch freight-scale tops if doorways or stairs cannot "
            "handle the shipment.",
        ),
        (
            "Electric vs manual sit-stand—what does this shortlist include?",
            "This shortlist is electric sit-stand desks with one-touch height adjustment and "
            "memory presets—not crank-only frames. Confirm motor and preset counts on the "
            "retailer page.",
        ),
    ],
    "cordless-vacuums": [
        (
            "Do I need an auto-empty dock on a cordless stick vac?",
            "Only if you hate emptying a bin and have floor space for a dock tower. Mid-chart "
            "sticks such as VortexIQ Pro lead when you want strong suction and anti-tangle "
            "without committing to an auto-empty dock.",
        ),
        (
            "Will a cordless stick handle carpet and hard floors?",
            "Yes—these are stick vacuums for quick carpet and hard-floor pickups, no robot "
            "required. Confirm runtime, bin emptying, and dock space on the retailer page.",
        ),
        (
            "How much runtime do I need?",
            "Skip a lower-priced anti-tangle stick if you need 60+ minute runtime or auto-empty. "
            "Confirm listed runtime on the retailer page against your floor plan.",
        ),
    ],
    "espresso-machines": [
        (
            "Do I need a built-in grinder on a home espresso machine?",
            "Only if you refuse a separate grinder. Gevi is the higher-priced bean-to-cup pick "
            "with conical burrs and a 20-bar pump. Skip it under a ~$200 budget or if you "
            "already own a good grinder.",
        ),
        (
            "Is a compact 20-bar wand machine enough?",
            "CM5418 is the most-reviewed compact 20-bar wand machine at the lowest verified "
            "price here. Skip it if you want a built-in grinder or a faster heat-up.",
        ),
        (
            "How much counter space do I need?",
            "Skip the Ultra-style LCD machine if counter space is tight—tank and footprint are "
            "larger. Confirm tank size, counter footprint, and grinder setup on the retailer page.",
        ),
    ],
    "air-fryers": [
        (
            "What size air fryer do I need for weeknight dinners?",
            "6–6.8 qt single-basket models cover most weeknight crisping without heating the "
            "whole oven. TwinFry’s 9 qt cavity with a removable divider is for two timings at "
            "once. Skip it if counter depth is tight.",
        ),
        (
            "Do I need dual heating or TurboBlaze?",
            "Dual heating cooks from the top and bottom so you shake less. TurboBlaze listings "
            "cite a high-speed fan and temperatures up to 450°F. Confirm basket capacity, "
            "counter depth, and footprint on the retailer page.",
        ),
        (
            "When should I skip a dual-zone air fryer?",
            "Skip a 9 qt double basket if you only cook one food at a time, or if you only want "
            "the cheapest ceramic basket that works.",
        ),
    ],
    "air-purifiers": [
        (
            "What CADR and room size should I match?",
            "Match claimed coverage to the room you will run it in—bedrooms, pet rooms, or "
            "open-plan spaces. Confirm room coverage, filter type, and noise rating on the "
            "retailer page.",
        ),
        (
            "Do I need a pet-specific air purifier?",
            "Vital Pet Pro leads the chart for pet homes: smart controls plus a heavy "
            "activated-carbon load aimed at dander and pet odor. Skip it if you need whole-home "
            "3-in-1 heat/cool purification.",
        ),
        (
            "How often do HEPA filters need replacing?",
            "Filter type and replacement interval are listing-specific. Confirm filter type and "
            "replacement cost on the retailer page before you buy.",
        ),
    ],
    "security-cameras": [
        (
            "Do I need solar outdoor cameras or a plug-in indoor cam?",
            "SoloCam S220 leads for wireless outdoor coverage with solar top-up and no mandatory "
            "monthly plan pitch on the card. Skip it if you only need a plug-in indoor pet cam.",
        ),
        (
            "When is a 2-cam outdoor kit worth it?",
            "The S340 2-cam kit is the higher-priced pick when one outdoor camera cannot cover "
            "driveway plus backyard. Skip it if a single outdoor cam already covers the entry.",
        ),
        (
            "Local storage vs a monthly plan?",
            "Indoor and solar outdoor cameras on this shortlist include local options and clear "
            "resolution tiers. Confirm power type, resolution, and storage plan on the retailer page.",
        ),
    ],
    "video-doorbells": [
        (
            "Battery or wired video doorbell?",
            "Battery models install wire-free and list up to about 10 months on a charge. Wired "
            "units need a compatible transformer. Confirm power type, field of view, and kit "
            "contents on the retailer page.",
        ),
        (
            "Do I need dual cameras for packages?",
            "E340 leads for porch packages: dual cameras (face-on plus downward package view), "
            "2K, and onboard storage. Skip it if you need HomeKit Secure Video as a hard requirement.",
        ),
        (
            "Does a video doorbell require a subscription?",
            "Several picks advertise onboard or hub storage with no mandatory monthly plan. "
            "Confirm local storage and any optional cloud plan on the retailer page.",
        ),
    ],
    "noise-cancelling-headphones": [
        (
            "Over-ear ANC for flights vs an open office?",
            "This shortlist is over-ear and travel ANC headphones for flights, open offices, and "
            "commute focus. Confirm ANC type, fit, and battery life on the retailer page.",
        ),
        (
            "How important is clamp comfort on long days?",
            "Clamp comfort, transparency mode, and battery life are the compare points on this "
            "chart. Open a deep review when two top scores look close, then confirm fit on the "
            "retailer page.",
        ),
        (
            "Do I need the most expensive ANC headphones?",
            "No. Score order currently leads with a lower-priced hybrid ANC pick. Confirm "
            "transparency and battery claims on the retailer listing before you buy.",
        ),
    ],
    "projectors": [
        (
            "Portable projector or living-room movie night?",
            "This shortlist covers portable and living-room projectors for movie nights without "
            "a giant TV buy. Confirm brightness, resolution, and throw distance on the retailer page.",
        ),
        (
            "How bright does a living-room projector need to be?",
            "Brightness and throw distance are listing-specific. Confirm lumens, resolution, and "
            "the distance you can sit from the wall on the retailer page.",
        ),
        (
            "Do I need 4K, or is 1080p enough?",
            "Match resolution to screen size and seating distance on the listing—not a lab claim. "
            "Confirm native resolution and input ports before you buy.",
        ),
    ],
    "massage-guns": [
        (
            "Who are these percussion massage guns for?",
            "Percussion recovery tools for athletes and desk stiffness, including FSA/HSA-friendly "
            "picks. Confirm heads, heat/cold options, and noise on the retailer page.",
        ),
        (
            "How many heads do I actually need?",
            "Head count and heat/cold options vary by listing. Confirm included heads and noise "
            "on the retailer page if you will use it in a shared room.",
        ),
        (
            "Can I use FSA or HSA on a massage gun?",
            "Some picks on this shortlist are listed as FSA/HSA-friendly. Confirm eligibility and "
            "the current offer on the retailer page—we do not process those cards.",
        ),
    ],
    "humidifiers": [
        (
            "Cool mist or warm mist for a bedroom?",
            "Levoit’s smart warm/cool mist leads for bedrooms that want both modes without a "
            "10 L refill chore. Skip a compact cool-mist unit if you need warm mist or app control.",
        ),
        (
            "What tank size do I need?",
            "A 6 L tank upgrades larger bedrooms with longer runtime. Skip it if a compact 3 L "
            "unit already covers your square footage. Confirm tank size, mist type, and room "
            "coverage on the retailer page.",
        ),
        (
            "Is a humidifier enough for a whole house?",
            "Skip these bedroom units if you need a whole-house evaporative tank over 20 L. "
            "This shortlist is ranked for bedrooms and larger living spaces, not whole-house HVAC.",
        ),
    ],
    "dehumidifiers": [
        (
            "What pint capacity and coverage do I need?",
            "Match pint/day and claimed square footage to the wet room. Skip a commercial 8000 "
            "sq ft class unit if Energy Star residential capacity is enough, or a 50-pint unit "
            "if it already keeps RH in range.",
        ),
        (
            "Do I need a drain hose, or is a tank enough?",
            "Energy Star basement and whole-home units on this chart include drain options. "
            "Confirm tank size, drain hose, and coverage sq ft on the retailer page.",
        ),
        (
            "When should I skip a large basement dehumidifier?",
            "Skip if you only need a small closet dehumidifier. Confirm humidity setpoints and "
            "auto-defrost on the retailer listing.",
        ),
    ],
    "tower-fans": [
        (
            "How quiet is a tower fan for a bedroom?",
            "Quiet tower and bladeless fans on this chart are ranked for bedrooms and living "
            "rooms. Confirm height, oscillation, and listed noise on the retailer page.",
        ),
        (
            "Do I need a smart tower fan?",
            "Levoit’s smart tower leads for bedrooms that want app or voice control with quiet "
            "sleep modes. Skip RGB or omni-directional extras if a simple remote tower is enough.",
        ),
        (
            "Tower vs bladeless—when does it matter?",
            "Skip a standard tower if you need a bladeless premium silhouette or adjustable-height "
            "design. Confirm CFM, oscillation coverage, and footprint on the retailer page.",
        ),
    ],
    "computer-speakers": [
        (
            "Studio monitors or casual desktop speakers?",
            "MR4.5 is the higher-priced pick for accuracy: bi-amped monitors with trim and DSP, "
            "not party RGB. Skip it if you only want casual multimedia speakers.",
        ),
        (
            "What wattage do I need at a desk?",
            "M60 leads for desk duty: 66W RMS multimedia power in a compact pair. Skip compact "
            "gaming RGB if you need 60W+ RMS for a larger room. Confirm wattage, inputs, and "
            "desk size on the retailer page.",
        ),
        (
            "Can I use these computer speakers outdoors?",
            "No. Skip this shortlist if you need Bluetooth-only portable speakers for outdoors— "
            "that is the Bluetooth speakers chart.",
        ),
    ],
    "bluetooth-speakers": [
        (
            "What should I look for in a portable Bluetooth speaker?",
            "This shortlist is ranked for home, patio, and travel—compare battery life, "
            "waterproofing, and real-world volume. Confirm output, battery life, and outdoor "
            "rating on the retailer page.",
        ),
        (
            "Do I need 80W patio volume?",
            "Boom 2 leads for outdoor and patio volume (about 80W with long playtime). Skip it "
            "if you need desk-bound powered computer speakers.",
        ),
        (
            "Can a shower speaker float?",
            "Select 4 Go is listed as a waterproof speaker designed to withstand harsh outdoor "
            "conditions and can even float. Confirm the IP rating on the retailer page.",
        ),
    ],
    "hair-dryers": [
        (
            "Do I need a high-speed ionic hair dryer?",
            "This shortlist ranks high-speed ionic dryers for everyday and travel drying. "
            "Compare wattage, heat-damage claims, and attachments. Confirm those on the "
            "retailer page.",
        ),
        (
            "What should travelers look for?",
            "Pocket Aura is the higher-priced pick for travelers and heat-sensitive routines. "
            "Laifen MINI listings cite an 8.58 × 2.40 × 2.99 inch carry-on size. Skip a "
            "standard high-speed dryer if you do not need smart heat.",
        ),
        (
            "Do I need a foldable dual-voltage dryer?",
            "Skip a diffuser-first everyday dryer if you need a foldable dual-voltage "
            "travel-first unit. Confirm attachments, dual-voltage, and heat settings on the "
            "retailer page.",
        ),
    ],
    "litter-boxes": [
        (
            "Do I need an AI camera on a self-cleaning litter box?",
            "Purobot Max Pro 2 is the higher-priced pick when litter duty includes AI camera "
            "monitoring and a larger opening for big cats. Skip it if a standard auto box "
            "without cameras is enough.",
        ),
        (
            "Open-top or enclosed for a large cat?",
            "Skip an enclosed odor-control box if you need an open-top design for very large "
            "cats. Confirm entry type, waste-bag setup, and size fit on the retailer page.",
        ),
        (
            "How quiet are automatic litter boxes at night?",
            "This shortlist ranks automatic boxes with odor control for multi-cat homes—compare "
            "cycle time, waste drawers, and quiet night modes. Confirm those on the retailer listing.",
        ),
    ],
    "dash-cams": [
        (
            "Front/rear or a 3-channel dash cam?",
            "F17 is the 4K 3-channel upgrade when rideshare, kids, or cabin events matter as "
            "much as the road. Skip it if front/rear only is enough.",
        ),
        (
            "Do I need STARVIS night sensors?",
            "4K front/rear and multi-channel units on this chart list STARVIS night sensors. "
            "Confirm channel count, cabin coverage, and card support on the retailer page.",
        ),
        (
            "What about parking mode and GPS?",
            "Compare parking mode, GPS, and buffered event recording on the listing. Confirm "
            "hardwire kit contents and card support before you buy.",
        ),
    ],
    "kids-bikes": [
        (
            "How do I size a kids bike?",
            "This shortlist is balance-to-pedal and lightweight kids bikes for beginners—size, "
            "weight, and grow-with-you features. Confirm wheel size, age range, and "
            "training-wheel setup on the retailer page.",
        ),
        (
            "Balance bike or pedal bike first?",
            "Balance-to-pedal frames are the grow-with-you option on this chart. Confirm the "
            "listed wheel size and whether training wheels are included before you buy.",
        ),
        (
            "Does a lighter kids bike matter?",
            "Yes for beginners who need to start and stop on their own. Confirm frame weight "
            "and age range on the retailer page—we do not invent lab weights.",
        ),
    ],
    "hearing-aids": [
        (
            "Are these over-the-counter hearing aids?",
            "This shortlist is OTC rechargeable hearing aids for everyday speech. Confirm "
            "prescription vs OTC labeling, return window, and fit on the retailer page.",
        ),
        (
            "Do I need a charging case?",
            "Most rechargeable pairs on this chart ship with a case. Confirm battery type, "
            "charge time, and case contents on the retailer listing before you buy.",
        ),
        (
            "Can I return a pair if the fit is wrong?",
            "Return windows vary by seller. Confirm fit style, trial period, and returns on "
            "the retailer page—we do not invent medical claims.",
        ),
    ],
    "water-filters": [
        (
            "Countertop RO or an under-sink system?",
            "This shortlist is complete water-filter systems—countertop RO, under-sink, and "
            "whole-house units. Skip replacement fridge cartridges; those are not on this chart.",
        ),
        (
            "Do I need a plumber?",
            "Many countertop units need no install. Under-sink and whole-house kits vary. "
            "Confirm install type and contents on the retailer page.",
        ),
        (
            "How often should I replace filters?",
            "Follow the listed month or gallon interval on the system. Confirm filter life "
            "and which stages ship in the box on the retailer page.",
        ),
    ],
    "under-sink-countertop-filtration": [
        (
            "Under-sink reverse osmosis or a countertop unit?",
            "This shortlist covers under-sink and countertop filtration systems. Confirm "
            "install type, tank vs tankless, and faucet finish on the retailer page.",
        ),
        (
            "Do I need a plumber for under-sink RO?",
            "Many tankless kits are DIY, but sink holes and drain saddles vary. Confirm "
            "install contents and faucet type on the listing.",
        ),
        (
            "How much space does an under-sink system need?",
            "Tankless units save cabinet space; tank systems need more. Confirm GPD rating "
            "and cabinet fit on the retailer page.",
        ),
    ],
    "pitcher-water-filters": [
        (
            "Electric pitcher or a standard gravity pitcher?",
            "This shortlist includes electric and replacement-filter pitchers. Confirm pitcher "
            "vs filter-only packs and stated filter life on the retailer page.",
        ),
        (
            "Will these filters fit a Brita pitcher?",
            "Some replacements list Brita-compatible fit. Confirm the pitcher model and "
            "filter SKU on the retailer page before you buy.",
        ),
        (
            "How long does a pitcher filter last?",
            "Life is listed in months or gallons on the pack. Confirm filter count and "
            "stated life on the retailer listing.",
        ),
    ],
    "doormats": [
        (
            "Indoor dirt-trapper or outdoor welcome mat?",
            "This shortlist is washable dirt-trapper and welcome doormats. Confirm indoor vs "
            "outdoor use and size on the retailer page.",
        ),
        (
            "What size doormat do I need?",
            "Common sizes on this chart are 24x36 and 36x60. Confirm width, depth, and "
            "door clearance on the listing.",
        ),
        (
            "Are these mats machine washable?",
            "Many dirt-trappers list washable construction. Confirm wash method and "
            "non-slip backing on the retailer page.",
        ),
    ],
    "split-system": [
        (
            "What BTU rating do I need?",
            "This shortlist is mini-split heating and cooling systems. Confirm BTU, SEER2, "
            "and voltage (115V vs 230V) on the retailer page.",
        ),
        (
            "Do I need a licensed installer?",
            "Line-set and electrical work often need a licensed HVAC tech. Confirm kit "
            "contents and install requirements on the listing.",
        ),
        (
            "Single-zone or multi-zone?",
            "Compare single-zone wall units vs multi-zone kits. Confirm zone count and "
            "outdoor-unit pairing on the retailer page.",
        ),
    ],
    "tv-wall-ceiling-mounts": [
        (
            "Full-motion or tilting TV mount?",
            "This shortlist is TV wall and ceiling mounts. Confirm motion type, TV size "
            "range, and VESA pattern on the retailer page.",
        ),
        (
            "Will this mount hold my TV weight?",
            "Weight and size ranges are listed per SKU. Confirm pounds, inch range, and "
            "stud vs drywall hardware on the listing.",
        ),
        (
            "Do I need an extension bracket?",
            "Some kits bundle slim mounts with extension brackets. Confirm depth, tilt, "
            "and hardware contents on the retailer page.",
        ),
    ],
    "monitor-arms": [
        (
            "Single arm or dual monitor mount?",
            "This shortlist is desk and wall monitor arms. Confirm single vs dual, screen "
            "size, and weight per arm on the retailer page.",
        ),
        (
            "Clamp or grommet install?",
            "Most desk arms ship with clamp and grommet options. Confirm desk thickness "
            "and reinforcement plate on the listing.",
        ),
        (
            "Will this hold an ultrawide?",
            "Ultrawide fit is listed in inches and VESA. Confirm VESA pattern and pound "
            "rating on the retailer page.",
        ),
    ],
    "stage-lights": [
        (
            "Par can wash or a moving head?",
            "This shortlist is DJ and stage wash lights. Confirm par vs moving head, pack "
            "count, and IP rating on the retailer page.",
        ),
        (
            "Do I need DMX control?",
            "Many packs list DMX and app modes. Confirm control options and power linking "
            "on the listing before you buy.",
        ),
        (
            "Indoor only or weather-resistant?",
            "Some pars list IP65 weather resistance. Confirm indoor vs outdoor rating and "
            "pack size on the retailer page.",
        ),
    ],
    "glass-display-cabinets": [
        (
            "Corner cabinet or a straight glass curio?",
            "This shortlist is glass display cabinets for collectibles. Confirm corner vs "
            "straight, tier count, and finish on the retailer page.",
        ),
        (
            "Do the LED lights need an outlet?",
            "RGB and sensor lights usually plug in. Confirm power type, sensor, and shelf "
            "weight rating on the listing.",
        ),
        (
            "How much assembly is required?",
            "Most curios ship flat-pack. Confirm dimensions, drawer count, and assembly "
            "notes on the retailer page.",
        ),
    ],
    "document-scanners": [
        (
            "Overhead book scanner or a sheet-fed scanner?",
            "This shortlist is overhead document and book scanners. Confirm camera MP, "
            "flattening cover, and software on the retailer page.",
        ),
        (
            "Do I need the assistive cover?",
            "Several kits bundle a flattening cover for curved pages. Confirm cover vs "
            "scanner-only contents on the listing.",
        ),
        (
            "Windows and Mac compatible?",
            "Compatibility is listed per model. Confirm OS support and included software "
            "on the retailer page before you buy.",
        ),
    ],
    "ceramic-space-heaters": [
        (
            "Will a 1500W ceramic heater cover a large room?",
            "The Premium card on this shortlist claims 270 sq.ft coverage with 70° "
            "oscillation. Compact bedside units are written for bedrooms and desks. "
            "Confirm wattage and claimed coverage on the retailer page before you buy.",
        ),
        (
            "Do I need 70° oscillation?",
            "Atom One and the Premium large-room card list 70° wide-angle oscillation "
            "for garages, basements, and offices. The compact white and Gold cards do "
            "not list that sweep. Skip oscillation if you only want a quiet bedside heater.",
        ),
        (
            "When should I skip a compact ceramic heater?",
            "Skip the compact white or Gold cards if you need garage or 270 sq.ft coverage. "
            "Those listings are the quiet 34dB / 1500W remote stack for bedrooms and offices, "
            "not a large-room default.",
        ),
        (
            "What should I confirm on the listing?",
            "Confirm wattage, oscillation, noise, tip-over protection, and that you can "
            "plug directly into a wall outlet — listings warn against extension cords.",
        ),
    ],
    "pillows": [
        (
            "Memory foam or down-alternative fill?",
            "This shortlist is bed pillows, not pillowcases or protectors. Confirm loft, "
            "fill, and firmness on the retailer page before you buy.",
        ),
        (
            "What loft should I pick?",
            "Loft and firmness should match how you sleep. We do not invent a padded "
            "Top 10 when a verified retail track is missing. Confirm loft on the listing.",
        ),
        (
            "Do I need a pair or a single pillow?",
            "Pack count is listing-specific. Confirm whether the offer is one pillow or "
            "a pair, plus the return window, on the retailer page.",
        ),
        (
            "What should I confirm on the listing?",
            "Confirm loft, fill, and firmness on the retailer page.",
        ),
    ],
    "mattresses": [
        (
            "Memory foam or a hybrid mattress?",
            "This shortlist is mattresses — not toppers, sheets, or foundations. Confirm "
            "size, firmness, and trial window on the retailer page.",
        ),
        (
            "What firmness works for most sleepers?",
            "Firmness is listing-specific. We do not invent a padded Top 10 when a "
            "verified retail track is missing. Confirm the listed feel before you buy.",
        ),
        (
            "Queen vs king — what changes?",
            "Size changes the box and the shipping path more than the feel. Confirm "
            "size and trial window on the retailer page.",
        ),
        (
            "What should I confirm on the listing?",
            "Confirm size, firmness, and trial window on the retailer page.",
        ),
    ],
    "office-chairs": [
        (
            "Mesh back or a cushioned executive chair?",
            "This shortlist is task and executive office chairs — not mats, casters, or "
            "lumbar pillows alone. Confirm lumbar support and seat depth on the listing.",
        ),
        (
            "Do I need adjustable lumbar support?",
            "Lumbar and arm adjustments are listing-specific. We do not invent a padded "
            "Top 10 when a verified retail track is missing. Confirm those controls "
            "on the retailer page.",
        ),
        (
            "What weight rating should I look for?",
            "Weight and seat-depth ratings vary by model. Confirm lumbar support, "
            "weight rating, and seat depth on the retailer page.",
        ),
        (
            "What should I confirm on the listing?",
            "Confirm lumbar support, weight rating, and seat depth on the retailer page.",
        ),
    ],
    "water-flossers": [
        (
            "Countertop reservoir or a cordless water flosser?",
            "This shortlist is complete water flossers — not replacement tips alone. "
            "Confirm tank size, pressure settings, and tip count on the retailer page.",
        ),
        (
            "Do I need a braces tip?",
            "Tip kits are listing-specific. We do not invent a padded Top 10 when a "
            "verified retail track is missing. Confirm whether a braces tip is in the box.",
        ),
        (
            "How many pressure settings do I need?",
            "Pressure and tank size vary by model. Confirm tank size, pressure settings, "
            "and tip count on the retailer page before you buy.",
        ),
        (
            "What should I confirm on the listing?",
            "Confirm tank size, pressure settings, and tip count on the retailer page.",
        ),
    ],
}

LANDING_FAQ_BLOCK = re.compile(
    r"(<h2>FAQ: buying .*?</h2>)(\s*(?:<details class=\"landing-faq\"[^>]*>.*?</details>\s*)+)",
    re.S,
)
CMP_FAQ_BLOCK = re.compile(
    r'(<div class="faq">\s*<h2>FAQ</h2>\s*)(.*?)(\s*</div>)',
    re.S,
)
DOCK_DETAILS = re.compile(
    r"<details[^>]*>\s*<summary>\s*Do I need the most automated dock\?\s*</summary>"
    r".*?</details>\s*",
    re.S | re.I,
)


def faqs_for(slug: str | None) -> list[tuple[str, str]]:
    if not slug:
        return []
    return list(CATEGORY_FAQS.get(slug) or [])


def _esc(text: str) -> str:
    return html.escape(text, quote=False)


def render_landing_details(faqs: list[tuple[str, str]]) -> str:
    parts: list[str] = []
    for i, (q, a) in enumerate(faqs):
        open_attr = " open" if i == 0 else ""
        parts.append(
            f'<details class="landing-faq"{open_attr}><summary>{_esc(q)}</summary> '
            f"<p>{_esc(a)}</p></details>"
        )
    return "\n        " + "\n        ".join(parts) + "\n        "


def render_cmp_details(faqs: list[tuple[str, str]]) -> str:
    parts: list[str] = []
    for i, (q, a) in enumerate(faqs):
        open_attr = " open" if i == 0 else ""
        parts.append(
            f"<details{open_attr}><summary>{_esc(q)}</summary>"
            f"<p>{_esc(a)}</p></details>"
        )
    return "\n          " + "\n".join(parts) + "\n        "


def faqpage_obj(faqs: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faqs
        ],
    }


def replace_faqpage_jsonld(html_text: str, faqs: list[tuple[str, str]]) -> str:
    script = (
        '<script type="application/ld+json">'
        + json.dumps(faqpage_obj(faqs), ensure_ascii=False, separators=(",", ":"))
        + "</script>"
    )
    found = False

    def _one(m: re.Match[str]) -> str:
        nonlocal found
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            return m.group(0)
        if data.get("@type") != "FAQPage":
            return m.group(0)
        found = True
        return script

    out = re.sub(
        r'<script type="application/ld\+json">(.*?)</script>',
        _one,
        html_text,
        flags=re.S,
    )
    if not found and faqs and "</head>" in out:
        out = out.replace("</head>", script + "\n</head>", 1)
    return out


def _replace_landing(html_text: str, faqs: list[tuple[str, str]]) -> str:
    def _block(m: re.Match[str]) -> str:
        return m.group(1) + render_landing_details(faqs)

    out, n = LANDING_FAQ_BLOCK.subn(_block, html_text, count=1)
    return out if n else html_text


def _replace_comparison(html_text: str, faqs: list[tuple[str, str]]) -> str:
    def _block(m: re.Match[str]) -> str:
        return m.group(1) + render_cmp_details(faqs) + m.group(3)

    out, n = CMP_FAQ_BLOCK.subn(_block, html_text, count=1)
    return out if n else html_text


def drop_dock_leftover(html_text: str) -> str:
    return DOCK_DETAILS.sub("", html_text)


def visible_faq_pairs(html_text: str) -> list[tuple[str, str]]:
    """Visitor FAQ widgets only — landing-faq or comparison .faq details."""
    pairs: list[tuple[str, str]] = []
    landing = re.findall(
        r'<details class="landing-faq"[^>]*>\s*<summary>(.*?)</summary>\s*(.*?)</details>',
        html_text,
        re.S,
    )
    cmp_m = CMP_FAQ_BLOCK.search(html_text)
    cmp_src = cmp_m.group(2) if cmp_m else ""
    cmp = re.findall(
        r"<details[^>]*>\s*<summary>(.*?)</summary>\s*(.*?)</details>",
        cmp_src,
        re.S,
    )
    for q_html, a_html in landing + cmp:
        q = re.sub(r"<[^>]+>", " ", q_html)
        q = html.unescape(re.sub(r"\s+", " ", q)).strip()
        a = re.sub(r"<[^>]+>", " ", a_html)
        a = html.unescape(re.sub(r"\s+", " ", a)).strip()
        if q and a:
            pairs.append((q, a))
    return pairs


def jsonld_faq_pairs(html_text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for blob in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html_text, re.S
    ):
        try:
            data = json.loads(blob)
        except json.JSONDecodeError:
            continue
        if data.get("@type") != "FAQPage":
            continue
        for ent in data.get("mainEntity") or []:
            if not isinstance(ent, dict):
                continue
            q = (ent.get("name") or "").strip()
            ans = ent.get("acceptedAnswer") or {}
            a = (ans.get("text") if isinstance(ans, dict) else "") or ""
            a = a.strip()
            if q and a:
                pairs.append((q, a))
    return pairs


def scrub_faqs(html_text: str, slug: str | None, kind: str | None = None) -> str:
    """Replace leftover / meta FAQs with category buyer Q&A. Unknown slugs drop dock leftover."""
    faqs = faqs_for(slug)
    if not faqs:
        html_text = drop_dock_leftover(html_text)
        return html_text

    landing_like = kind == "landing" or (kind is None and 'class="landing-faq"' in html_text)
    cmp_like = kind == "comparison" or (
        kind is None and '<div class="faq">' in html_text and "cmp-howto" in html_text
    )
    if landing_like:
        html_text = _replace_landing(html_text, faqs)
    if cmp_like:
        html_text = _replace_comparison(html_text, faqs)
    if landing_like or cmp_like:
        html_text = replace_faqpage_jsonld(html_text, faqs)
    if slug not in KEEP_ROBOT_VAC_SLUGS:
        html_text = drop_dock_leftover(html_text)
    return html_text


def scrub_site(site: Path) -> dict[str, int]:
    from site_config import ALL_CATS  # local import — stdlib script

    changed: dict[str, int] = {}
    for cat in ALL_CATS:
        slug = cat.get("slug")
        if not slug:
            continue
        for rel in (Path(slug) / "index.html", Path(slug) / "comparison" / "index.html"):
            path = site / rel
            if not path.is_file():
                continue
            kind = "comparison" if rel.as_posix().endswith("comparison/index.html") else "landing"
            html_text = path.read_text(encoding="utf-8")
            out = scrub_faqs(html_text, slug, kind=kind)
            if out != html_text:
                path.write_text(out, encoding="utf-8")
                changed[str(rel)] = 1
    return changed


def _faq_blob(pairs: list[tuple[str, str]]) -> str:
    return " ".join(f"{q} {a}" for q, a in pairs).lower()


def site_errors(site: Path) -> list[str]:
    from site_config import ALL_CATS  # local import

    errors: list[str] = []
    for cat in ALL_CATS:
        slug = cat["slug"]
        for label, rel in (
            ("landing", Path(slug) / "index.html"),
            ("comparison", Path(slug) / "comparison" / "index.html"),
        ):
            path = site / rel
            if not path.is_file():
                errors.append(f"missing {label} {rel}")
                continue
            html_text = path.read_text(encoding="utf-8")
            visible = visible_faq_pairs(html_text)
            expected = faqs_for(slug)
            blob = _faq_blob(visible)
            if not expected:
                continue
            if len(visible) < 3 or len(visible) > 5:
                errors.append(f"{slug} {label} FAQ count={len(visible)} (need 3–5)")
            vis_q = [q.lower() for q, _ in visible]
            for q, a in expected:
                if q.lower() not in vis_q:
                    errors.append(f"{slug} {label} missing buyer FAQ: {q}")
            for meta in META_FAQ_PHRASES:
                if meta in blob:
                    errors.append(f"{slug} {label} still has meta FAQ: {meta}")
            if slug in KEEP_ROBOT_VAC_SLUGS:
                if DOCK_Q.lower() not in vis_q:
                    errors.append(f"{slug} {label} lost native dock FAQ")
            else:
                for phrase in DOCK_PHRASES:
                    if phrase in html_text.lower():
                        errors.append(f"{slug} {label} still has robot-vac leftover: {phrase}")
            ld = jsonld_faq_pairs(html_text)
            if [(q, a) for q, a in ld] != [(q, a) for q, a in visible]:
                errors.append(f"{slug} {label} FAQPage JSON-LD does not match visible FAQ")
            comm = "do you earn a commission" in blob or "we may earn an affiliate commission" in blob
            if comm and "advertising disclosure" not in blob:
                # commission text inside FAQ answers is blocked; sidebar disclosure is fine
                if any("commission" in (a.lower()) for _, a in visible):
                    errors.append(f"{slug} {label} FAQ still talks commission")
    return errors


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    site = root / "site"
    changed = scrub_site(site)
    errors = site_errors(site)
    print(f"scrubbed {len(changed)} FAQ pages")
    for rel in sorted(changed):
        print(f"  {rel}")
    if errors:
        raise SystemExit("landing_faq verify failed:\n- " + "\n- ".join(errors))
    print("landing_faq ok")


if __name__ == "__main__":
    main()
