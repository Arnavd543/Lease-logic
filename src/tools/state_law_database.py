import json
from typing import List, Dict
from pathlib import Path
import os

class StateLawDatabase:
    """Manages tenant protection laws for multiple states + federal"""
    
    # Top states by renter population
    SUPPORTED_STATES = [
        "california",
        "new_york", 
        "texas",
        "florida",
        "illinois",
        "washington",
        "massachusetts"
    ]
    
    def __init__(self):
        self.laws_by_state = {}
        self.federal_laws = []
    
    def get_california_laws(self) -> List[Dict]:
        """California Civil Code 1940-1954"""
        return [
            {
                "section": "1940",
                "title": "Definitions - Hiring of Real Property",
                "text": """The hiring of real property is a transfer of a less than total interest in the property. The landlord (lessor) and tenant (lessee) have distinct rights and obligations defined by this code and the rental agreement. Unless modified by the rental agreement, the Civil Code governs the landlord-tenant relationship.""",
                "category": "definitions",
                "state": "california",
                "jurisdiction": "state"
            },
            {
                "section": "1941",
                "title": "Landlord Duty to Repair",
                "text": """The landlord must: (1) Put the premises in a habitable condition at the beginning of the tenancy, and (2) Repair all subsequent dilapidations that render the property untenantable. Habitable conditions include effective waterproofing, plumbing, heating, electrical lighting, clean and sanitary conditions, and adequate trash receptacles.""",
                "category": "habitability",
                "state": "california",
                "jurisdiction": "state"
            },
            {
                "section": "1941.1",
                "title": "Untenantable Dwelling - Specific Requirements",
                "text": """A dwelling is legally untenantable if it substantially lacks any of the following: effective waterproofing and weather protection of roof and exterior walls; plumbing facilities in good working order (including hot and cold running water and sewage disposal); gas facilities in good working order; heating facilities in good working order; electrical lighting with wiring and outlets in good working order; building/grounds kept clean and sanitary and free from debris, filth, rubbish, garbage, rodents, and vermin; adequate number of trash receptacles in good repair; floors, stairways, and railings in good repair; or compliance with applicable building codes materially affecting health and safety.""",
                "category": "habitability",
                "state": "california",
                "jurisdiction": "state"
            },
            {
                "section": "1942",
                "title": "Tenant Remedies for Uninhabitable Conditions",
                "text": """If the landlord fails to repair dilapidations rendering the premises untenantable within a reasonable time after written notice from the tenant, the tenant may: (1) Abandon the premises and be discharged from further rent payment, OR (2) Continue occupancy and either repair the defects themselves and deduct the cost from rent (not exceeding one month's rent), OR withhold rent. The tenant must provide written notice to the landlord of the defects and give reasonable time to repair (typically 30 days for non-emergency issues).""",
                "category": "remedies",
                "state": "california",
                "jurisdiction": "state"
            },
            {
                "section": "1946",
                "title": "Termination of Month-to-Month Tenancy - Notice Period",
                "text": """A month-to-month residential tenancy may be terminated by either party giving written notice at least 30 days before the next rent due date. However, if the tenant has resided in the dwelling for one year or more, the landlord must provide at least 60 days notice. The tenant is only required to give 30 days notice regardless of length of tenancy.""",
                "category": "termination",
                "state": "california",
                "jurisdiction": "state"
            },
            {
                "section": "1946.1",
                "title": "Landlord Termination Notice Requirements",
                "text": """When a landlord terminates a month-to-month tenancy, they must provide at least 60 days written notice if the tenant has resided in the dwelling for one year or more. 30 days notice is required if the tenancy is less than one year. The notice must be in writing and properly served. Just cause termination requirements may apply in rent-controlled jurisdictions.""",
                "category": "termination",
                "state": "california",
                "jurisdiction": "state"
            },
            {
                "section": "1950.5",
                "title": "Security Deposits - Limits and Return",
                "text": """Maximum security deposits: For unfurnished units, the total security deposit (including last month's rent) cannot exceed two months' rent. For furnished units, it cannot exceed three months' rent. The landlord must return the deposit within 21 days after the tenant vacates, along with an itemized statement of any deductions. Allowable deductions are limited to: (1) unpaid rent, (2) cleaning costs to restore the unit to its original condition (excluding normal wear and tear), and (3) repair costs for damages beyond normal wear and tear. If the landlord fails to return the deposit or provide an itemized statement within 21 days, the tenant may be entitled to the full deposit amount plus damages.""",
                "category": "security_deposit",
                "state": "california",
                "jurisdiction": "state"
            },
            {
                "section": "1954",
                "title": "Landlord Right of Entry - Notice Requirements",
                "text": """A landlord may enter a dwelling unit only in the following cases: (1) In case of emergency, (2) To make necessary or agreed-upon repairs, decorations, alterations, or improvements, (3) To show the property to prospective buyers, tenants, lenders, or contractors, (4) When the tenant has abandoned or surrendered the premises, or (5) Pursuant to court order. Except in cases of emergency or abandonment, entry is only permitted during normal business hours and the landlord must give the tenant reasonable notice in writing (generally 24 hours is considered reasonable). The notice must specify the date, approximate time, and purpose of entry. The landlord shall not abuse the right of access or use it to harass the tenant.""",
                "category": "entry_notice",
                "state": "california",
                "jurisdiction": "state"
            },
            {
                "section": "1940.2",
                "title": "Late Fees - Reasonableness Requirement",
                "text": """Late fees charged for late payment of rent must be reasonable and specifically authorized in the written rental agreement or lease. California courts have generally found late fees exceeding 5-6% of monthly rent to be potentially unreasonable. The fee must reasonably relate to the landlord's actual costs incurred due to late payment. Late fees cannot be charged until rent is at least 3-5 days late (depending on lease terms). Excessive late fees may be deemed unenforceable as a penalty rather than liquidated damages.""",
                "category": "fees",
                "state": "california",
                "jurisdiction": "state"
            },
            {
                "section": "1942.5",
                "title": "Retaliation Prohibited",
                "text": """It is unlawful for a landlord to retaliate against a tenant who has: (1) Complained to the landlord or a government agency about habitability issues, (2) Lawfully organized or participated in a tenant organization, or (3) Exercised any rights under the law. Retaliatory actions include increasing rent, decreasing services, causing the tenant to quit involuntarily, threatening to file an eviction action, or filing an eviction action. There is a rebuttable presumption of retaliation if the landlord takes action within 180 days of the tenant exercising their rights.""",
                "category": "retaliation",
                "state": "california",
                "jurisdiction": "state"
            },
            {
                "section": "1951.2",
                "title": "Damages for Breach - Early Lease Termination",
                "text": """When a tenant breaches a lease by moving out early, the landlord is entitled to damages equal to: (1) The worth of unpaid rent that was due before tenant left, plus (2) The worth of the amount by which unpaid rent for the remainder of the lease term exceeds the amount of rental loss that could have been reasonably avoided. The landlord has a duty to mitigate damages by making reasonable efforts to re-rent the property. The tenant is not liable for rent during any period the landlord could have reasonably re-rented the property.""",
                "category": "termination",
                "state": "california",
                "jurisdiction": "state"
            },
            {
                "section": "789.3",
                "title": "Unlawful Landlord Actions - Utility Shutoffs",
                "text": """A landlord shall not, with intent to terminate occupancy, willfully: (1) Prevent the tenant from gaining reasonable access to the property, (2) Remove doors, windows, or locks, (3) Remove tenant's personal property unless authorized by court order, or (4) Interrupt or cause interruption of utility services (water, heat, light, electricity, gas, telephone, elevator, or refrigeration). Violation subjects the landlord to civil penalties of up to $100 per day for each violation, and the tenant may recover actual damages or $100 per day of violation (whichever is greater), plus attorney's fees. This is considered a form of unlawful self-help eviction.""",
                "category": "unlawful_actions",
                "state": "california",
                "jurisdiction": "state"
            }
        ]
    
    def get_new_york_laws(self) -> List[Dict]:
        """New York Real Property Law & Rent Stabilization Code"""
        return [
            {
                "section": "RPL 235-b",
                "title": "Security Deposits - Requirements and Limits",
                "text": """Maximum security deposit: one month's rent. Landlord must deposit in interest-bearing account in New York bank. Interest must be paid to tenant annually or applied to rent. Landlord must provide tenant with receipt and name/address of bank within 30 days. Deposit must be returned within 14 days after tenant vacates, with itemized statement of deductions. Failure to comply allows tenant to recover deposit plus damages and attorney fees.""",
                "category": "security_deposit",
                "state": "new_york",
                "jurisdiction": "state"
            },
            {
                "section": "RPL 235-e",
                "title": "Retaliatory Eviction Prohibited",
                "text": """Landlord cannot evict or refuse to renew lease in retaliation for tenant: (1) complaining to government agency about violations, (2) joining or organizing tenant organization, or (3) exercising rights under law. Presumption of retaliation if action taken within 6 months of protected activity. Landlord must prove legitimate, non-retaliatory reason.""",
                "category": "retaliation",
                "state": "new_york",
                "jurisdiction": "state"
            },
            {
                "section": "RPL 235-f",
                "title": "Notice to Quit Requirements",
                "text": """For month-to-month tenancies: landlord must give one month notice. For tenancies of one year or more: 30 days notice required. For tenancies of less than one year but more than one month: notice equal to tenancy period required. Notice must be in writing and properly served. In NYC rent stabilized units, additional just cause requirements apply.""",
                "category": "termination",
                "state": "new_york",
                "jurisdiction": "state"
            },
            {
                "section": "RPAPL 711",
                "title": "Grounds for Eviction - Legal Requirements",
                "text": """Landlord may evict only for: (1) non-payment of rent, (2) violation of substantial obligation of tenancy, (3) holdover after lease expiration, (4) nuisance, (5) illegal use of premises, (6) owner occupancy (with restrictions), or (7) refusal to renew lease (where allowed). Must follow formal court procedures through Housing Court. No self-help evictions - landlord cannot lock out tenant or remove belongings without court order.""",
                "category": "eviction",
                "state": "new_york",
                "jurisdiction": "state"
            },
            {
                "section": "RPL 235-a",
                "title": "Warrant of Habitability - Implied Warranty",
                "text": """Every residential lease includes implied warranty that premises are fit for human habitation. Landlord must maintain in good repair: (1) all facilities for heat, hot water, and water, (2) all facilities for electricity, gas, and ventilation, (3) safe electrical, plumbing, sanitary, heating systems, and (4) floors, stairways, railings free from dangerous conditions. Breach of warranty allows tenant remedies including rent reduction, repair and deduct, or lease termination.""",
                "category": "habitability",
                "state": "new_york",
                "jurisdiction": "state"
            },
            {
                "section": "NYC Admin Code 27-2005",
                "title": "Heat and Hot Water Requirements",
                "text": """From October 1 through May 31, landlord must provide: (1) Heat to at least 68°F when outside temperature falls below 55°F during day (6 AM - 10 PM), and (2) Heat to at least 62°F at night (10 PM - 6 AM). Hot water must be provided 365 days per year at minimum 120°F. Violations subject to significant fines.""",
                "category": "habitability",
                "state": "new_york",
                "jurisdiction": "state"
            },
            {
                "section": "RPL 234",
                "title": "Right to Sublease",
                "text": """In buildings with four or more units, tenant has right to sublease with landlord's consent. Landlord cannot unreasonably withhold consent. Tenant must provide landlord written request with information about proposed sublessee. Landlord has 30 days to consent or provide reasonable objection. If landlord unreasonably refuses, tenant may sublet or terminate lease. Landlord cannot charge more than $50 to process sublease request.""",
                "category": "tenancy_rights",
                "state": "new_york",
                "jurisdiction": "state"
            },
            {
                "section": "Rent Stabilization Code 2524.2",
                "title": "Rent Increase Limitations - Stabilized Units",
                "text": """For rent-stabilized apartments (built before 1974 or receiving tax benefits), rent increases limited to rates set annually by Rent Guidelines Board. One-year lease renewals and two-year renewals have different percentage caps. Landlord can increase only at lease renewal. Individual apartment improvements may justify additional increases with proper documentation. Major Capital Improvements (MCI) increases require DHCR approval.""",
                "category": "rent_control",
                "state": "new_york",
                "jurisdiction": "state"
            },
            {
                "section": "RPL 231",
                "title": "Landlord's Duty to Provide Services",
                "text": """Landlord must provide all services and facilities required by lease, including heat, hot water, elevator service, garbage removal, and security services where applicable. Reduction or elimination of required services constitutes breach of lease. Tenant can file complaint with DHCR for service reduction and may receive rent reduction until services restored.""",
                "category": "habitability",
                "state": "new_york",
                "jurisdiction": "state"
            },
            {
                "section": "NYC Admin Code 27-2140",
                "title": "Window Guards Required",
                "text": """In buildings with three or more apartments, landlord must provide window guards if child under 10 years old resides in building. Landlord must annually notify tenants of availability and install upon request. Applies to all windows, including first floor, except fire escape access windows. Failure to comply subjects landlord to fines.""",
                "category": "habitability",
                "state": "new_york",
                "jurisdiction": "state"
            }
        ]
    
    def get_texas_laws(self) -> List[Dict]:
        """Texas Property Code Chapter 92"""
        return [
            {
                "section": "92.102",
                "title": "Security Deposit Refund Requirements",
                "text": """Landlord must return deposit within 30 days after tenant vacates and surrenders possession. Must provide written itemized list of deductions. If landlord fails to return deposit or provide list within 30 days, landlord forfeits right to withhold any portion and is liable for tenant's $100 plus three times deposit amount, plus attorney fees. Tenant must provide forwarding address in writing to receive refund.""",
                "category": "security_deposit",
                "state": "texas",
                "jurisdiction": "state"
            },
            {
                "section": "92.109",
                "title": "Security Deposit Interest Not Required",
                "text": """Texas law does not require landlords to pay interest on security deposits (unlike California, New York, and some other states). Unless lease specifically requires it, landlord may hold deposit in non-interest bearing account.""",
                "category": "security_deposit",
                "state": "texas",
                "jurisdiction": "state"
            },
            {
                "section": "92.052",
                "title": "Landlord Duty to Repair and Remedy",
                "text": """Landlord must make reasonable repairs within 7 days (or as soon as practicable) after receiving written notice from tenant of conditions materially affecting health or safety. If landlord fails to repair, tenant may: (1) terminate lease, (2) repair and deduct from rent, (3) reduce rent based on reduced rental value, or (4) obtain civil remedies including damages, court costs, and attorney fees. Conditions must materially affect physical health or safety of ordinary tenant.""",
                "category": "habitability",
                "state": "texas",
                "jurisdiction": "state"
            },
            {
                "section": "92.019",
                "title": "Landlord's Entry - Notice Requirements",
                "text": """Landlord may enter dwelling without notice only in emergencies or if tenant has abandoned premises. For all other entries, landlord must give at least 24 hours notice before entry. Notice may be written or oral unless lease requires written notice. Entry must be at reasonable times. Purposes for entry include: repairs, showing to prospective tenants/buyers, or inspection. Landlord cannot abuse right of entry.""",
                "category": "entry_notice",
                "state": "texas",
                "jurisdiction": "state"
            },
            {
                "section": "92.006",
                "title": "Residential Lease Required Provisions",
                "text": """Every residential lease must include: (1) landlord's name, address, and phone number, (2) name and address of managing agent if different from landlord, and (3) if applicable, statement that property is located in 100-year floodplain. Oral leases are valid but written leases provide better protection and are required for leases over one year.""",
                "category": "lease_requirements",
                "state": "texas",
                "jurisdiction": "state"
            },
            {
                "section": "92.059",
                "title": "Landlord Liability for Personal Injury",
                "text": """Landlord is liable for personal injury resulting from condition of premises if: (1) landlord was negligent, (2) condition was result of landlord's failure to repair or remedy, and (3) landlord had knowledge of dangerous condition. Landlord must address known hazards that materially affect health or safety. Includes conditions like broken stairs, inadequate locks on entry doors, or known criminal activity on property requiring security measures.""",
                "category": "liability",
                "state": "texas",
                "jurisdiction": "state"
            },
            {
                "section": "92.331",
                "title": "Removal of Tenant Property - Requirements",
                "text": """After tenant abandons property, landlord must store tenant's personal property and deliver written notice to tenant. If property value exceeds $3,000, must store for 60 days. If less than $3,000, must store for 30 days. Notice must state landlord's name, address, description of property, and where stored. After storage period expires and tenant doesn't claim property, landlord may dispose of items. Cannot dispose before deadlines.""",
                "category": "eviction",
                "state": "texas",
                "jurisdiction": "state"
            },
            {
                "section": "92.008",
                "title": "Landlord Retaliation Prohibited",
                "text": """Landlord cannot retaliate against tenant for: (1) complaining to landlord about condition materially affecting health or safety, (2) complaining to government agency about violation, or (3) exercising rights under lease or law. Retaliatory action includes eviction, refusing to renew, causing material decrease in services, or increasing rent. Presumption of retaliation if action within 6 months of tenant's complaint. Landlord must prove legitimate, non-retaliatory reason.""",
                "category": "retaliation",
                "state": "texas",
                "jurisdiction": "state"
            },
            {
                "section": "92.0081",
                "title": "Landlord Duty Regarding Smoke Alarms",
                "text": """Landlord must install smoke alarms in accordance with building code outside each bedroom, on each floor, and in each unit. Must ensure smoke alarms in working condition at beginning of lease. Tenant must pay for batteries during tenancy. If tenant notifies landlord of malfunction, landlord must repair/replace within 7 days. Landlord not liable if tenant removes batteries or disables alarm.""",
                "category": "habitability",
                "state": "texas",
                "jurisdiction": "state"
            },
            {
                "section": "92.01",
                "title": "Notice to Vacate Requirements",
                "text": """To terminate month-to-month tenancy, either party must give at least one month notice before termination date. Notice must be in writing. For week-to-week tenancy, one week notice required. For day-to-day tenancy, notice not required. Fixed-term leases automatically terminate at end of term unless renewed. Early termination without cause requires landlord consent unless lease permits.""",
                "category": "termination",
                "state": "texas",
                "jurisdiction": "state"
            }
        ]
    
    def get_florida_laws(self) -> List[Dict]:
        """Florida Statutes Chapter 83 Part II"""
        return [
            {
                "section": "83.49",
                "title": "Security Deposits - Holding and Return",
                "text": """Landlord must return deposit within 15 days if no deductions, or within 30 days if making deductions (must provide itemized list by certified mail). Deposit must be held in Florida financial institution, either in separate account or posted bond. Interest not required unless stated in lease. If landlord sells property, deposit must be transferred to new owner with tenant notification. Tenant forfeits right to dispute deductions if doesn't object within 15 days of receiving itemization.""",
                "category": "security_deposit",
                "state": "florida",
                "jurisdiction": "state"
            },
            {
                "section": "83.51",
                "title": "Landlord's Obligation to Maintain Premises",
                "text": """Landlord must: (1) comply with building, housing, and health codes, (2) maintain roof, windows, doors, floors, and exterior walls in good repair, (3) maintain plumbing in reasonable working condition, (4) provide functioning facilities for heat during winter, running water, and hot water, (5) maintain common areas in clean and safe condition, (6) provide and maintain garbage receptacles, (7) provide locks and keys, (8) exterminate bedbugs, rats, and other pests (except roaches and ants - shared responsibility). Landlord has 7 days to repair after written notice, or 20 days for conditions not threatening health/safety.""",
                "category": "habitability",
                "state": "florida",
                "jurisdiction": "state"
            },
            {
                "section": "83.53",
                "title": "Notice to Terminate Tenancy - Time Periods",
                "text": """Notice requirements vary by tenancy type: Year-to-year tenancy requires 60 days notice before end of year. Quarter-to-quarter requires 30 days. Month-to-month requires 15 days. Week-to-week requires 7 days. Notice must be in writing and delivered properly. Fixed-term leases end automatically unless lease requires notice. Landlord may require tenant to give 60 days notice if lease is for at least one year.""",
                "category": "termination",
                "state": "florida",
                "jurisdiction": "state"
            },
            {
                "section": "83.67",
                "title": "Prohibited Landlord Actions - No Self-Help Eviction",
                "text": """Landlord cannot: (1) remove outside doors, locks, roof, walls, or windows except for repairs, (2) remove tenant's possessions, (3) shut off utilities including water, heat, light, electricity, gas, elevator, garbage collection, or refrigeration, (4) prevent tenant from reasonable access to premises. These actions constitute unlawful self-help eviction. Landlord must use formal court eviction process. Violation allows tenant to recover actual damages or three months rent, whichever is greater, plus attorney fees.""",
                "category": "unlawful_actions",
                "state": "florida",
                "jurisdiction": "state"
            },
            {
                "section": "83.63",
                "title": "Casualty Damage - Tenant Rights",
                "text": """If premises destroyed or damaged by fire or casualty making premises uninhabitable, tenant may immediately vacate and written notice to landlord terminates lease. Tenant liable only for proportionate rent through date of casualty. If damage is such that enjoyment substantially impaired but premises remain habitable, tenant may immediately vacate, give written notice, and terminate lease or vacate and reduce rent proportionately. Landlord has reasonable time to repair.""",
                "category": "tenancy_rights",
                "state": "florida",
                "jurisdiction": "state"
            },
            {
                "section": "83.56",
                "title": "Landlord's Access to Dwelling - Notice Required",
                "text": """Landlord may enter dwelling with 12 hours notice for: (1) inspection, (2) making repairs, (3) showing premises to prospective tenants during final two weeks before termination. In emergencies, may enter without notice. If tenant unreasonably withholds consent to enter, landlord may obtain court order. Landlord cannot abuse right of access or use it to harass tenant. Entry must be during reasonable hours unless emergency.""",
                "category": "entry_notice",
                "state": "florida",
                "jurisdiction": "state"
            },
            {
                "section": "83.595",
                "title": "Choice of Remedies for Landlord",
                "text": """When tenant breaches lease, landlord may: (1) terminate lease by giving written notice and file eviction action if tenant doesn't vacate, (2) retake possession and re-rent premises while holding tenant liable for unpaid rent minus rent received from new tenant, or (3) stand by and do nothing while rent accrues. Landlord has duty to mitigate damages by attempting to re-rent. Cannot pursue both eviction and damages for future rent simultaneously - must elect remedy.""",
                "category": "eviction",
                "state": "florida",
                "jurisdiction": "state"
            },
            {
                "section": "83.57",
                "title": "Termination of Tenancy with Specific Cause",
                "text": """Landlord may terminate for: (1) failure to pay rent (must give 3 days notice), (2) material breach of lease other than rent (7 days notice with opportunity to cure, or immediate notice if breach cannot be cured such as illegal activity), (3) repeated violations of same lease clause (7 days notice without opportunity to cure after initial violation). Notice must be in writing. If tenant doesn't cure or vacate, landlord must file formal eviction action.""",
                "category": "eviction",
                "state": "florida",
                "jurisdiction": "state"
            },
            {
                "section": "83.682",
                "title": "Escrow Deposit for Alleged Uninhabitable Conditions",
                "text": """If landlord fails to maintain premises in habitable condition, tenant may deposit rent with court clerk. Tenant must notify landlord of noncompliance and intent to deposit rent into registry if not remedied within 7 days. After depositing rent, court will hold hearing. If landlord prevails, rent disbursed to landlord. If tenant prevails, court may disburse funds for repairs, order rent reduction, or terminate lease. Protects tenant from eviction for non-payment while pursuing habitability claims.""",
                "category": "remedies",
                "state": "florida",
                "jurisdiction": "state"
            },
            {
                "section": "83.46",
                "title": "Prohibited Provisions in Rental Agreements",
                "text": """Lease provision is void and unenforceable if it: (1) waives tenant's right to habitability, (2) requires tenant to pay landlord's attorney fees without reciprocal provision, (3) allows landlord to terminate for tenant's calling police or emergency services, (4) authorizes eviction without court process, or (5) waives tenant's rights under Chapter 83. Any unconscionable provision is unenforceable. Presence of illegal provision doesn't invalidate entire lease - only illegal provision is void.""",
                "category": "lease_requirements",
                "state": "florida",
                "jurisdiction": "state"
            }
        ]
    
    def get_illinois_laws(self) -> List[Dict]:
        """Illinois Compiled Statutes 765 ILCS 705 & 710"""
        return [
            {
                "section": "765 ILCS 710/1",
                "title": "Security Deposit Return Act - Requirements",
                "text": """Landlord must return security deposit within 45 days after tenant vacates (30 days if lease was for less than 6 months). Must provide itemized statement of deductions within same period. If landlord fails to return deposit or provide statement within required time, forfeits right to retain any portion of deposit and may be liable for two times deposit amount plus court costs and attorney fees. Applies to buildings with 5 or more units in cities over 25,000 population.""",
                "category": "security_deposit",
                "state": "illinois",
                "jurisdiction": "state"
            },
            {
                "section": "765 ILCS 715",
                "title": "Security Deposit Interest Requirements",
                "text": """In cities over 25,000 population, landlord of building with 25+ units must pay interest on security deposits. Interest must be paid annually or applied to rent. Rate is determined by ordinance or set amount. Landlord must provide receipt for deposit and specify where deposited. Tenant entitled to interest accrued from date deposit paid, not from lease start. Failure to pay interest allows tenant to deduct from rent.""",
                "category": "security_deposit",
                "state": "illinois",
                "jurisdiction": "state"
            },
            {
                "section": "765 ILCS 705/2",
                "title": "Retaliatory Conduct Prohibited",
                "text": """Landlord cannot evict, refuse to renew, increase rent, or decrease services in retaliation for tenant: (1) complaining to landlord about violations, (2) complaining to government agency, (3) organizing or joining tenant union, or (4) exercising rights under lease or law. Presumption of retaliation if action within one year of protected activity. Landlord can overcome presumption by showing action taken in good faith.""",
                "category": "retaliation",
                "state": "illinois",
                "jurisdiction": "state"
            },
            {
                "section": "735 ILCS 5/9-207",
                "title": "Notice to Terminate Periodic Tenancy",
                "text": """Week-to-week tenancy requires 7 days notice. Month-to-month requires 30 days notice (60 days in Chicago for units subject to Chicago RLTO). Year-to-year requires 60 days notice. Notice must be in writing and expire on last day of rental period. Landlord terminating month-to-month in Chicago must provide just cause or property exemption under ordinance.""",
                "category": "termination",
                "state": "illinois",
                "jurisdiction": "state"
            },
            {
                "section": "765 ILCS 705/1",
                "title": "Tenant Remedies for Landlord Violations",
                "text": """If landlord violates security deposit law, fails to maintain premises, or breaches lease, tenant may: (1) terminate lease and vacate, (2) repair and deduct from rent (up to $500 or half month's rent), (3) reduce rent to reflect reduced value, (4) sue for breach of contract, or (5) report to government enforcement agency. Must provide written notice to landlord and reasonable time to remedy before pursuing remedies.""",
                "category": "remedies",
                "state": "illinois",
                "jurisdiction": "state"
            },
            {
                "section": "735 ILCS 5/9-213.1",
                "title": "Eviction Procedures - Forcible Entry and Detainer",
                "text": """Landlord must use court process to evict. Cannot forcibly remove tenant or possessions without court order. Must file complaint in circuit court, tenant receives summons, court holds hearing. If landlord prevails, court issues eviction order. Sheriff enforces eviction. Self-help evictions (lockouts, utility shutoffs, removing belongings) are illegal. Tenant may sue for wrongful eviction and recover damages, attorney fees, and costs.""",
                "category": "eviction",
                "state": "illinois",
                "jurisdiction": "state"
            },
            {
                "section": "765 ILCS 742",
                "title": "Rent Payment - Receipt Requirements",
                "text": """Upon request, landlord must provide written receipt for rent payment. Receipt must include: date, amount, rental period, tenant name, property address. If landlord refuses to provide receipt, tenant may withhold rent payment. Landlord cannot charge fee for providing receipt. Applies to all residential leases in Illinois.""",
                "category": "lease_requirements",
                "state": "illinois",
                "jurisdiction": "state"
            },
            {
                "section": "765 ILCS 730",
                "title": "Heating Requirements - Adequate Heat",
                "text": """Between September 15 and June 1, landlord must provide adequate heat to maintain temperature of 68°F when outside temperature falls below 55°F. Heat must be available 24 hours per day during heating season. Failure to provide adequate heat constitutes violation and tenant may pursue remedies including rent reduction, repair and deduct, or lease termination. Does not apply if tenant controls and pays for heat directly.""",
                "category": "habitability",
                "state": "illinois",
                "jurisdiction": "state"
            },
            {
                "section": "765 ILCS 750",
                "title": "Carbon Monoxide Alarm Requirements",
                "text": """Landlord must install approved carbon monoxide alarm within 15 feet of every room used for sleeping. Alarm required in units with fuel-burning appliances or attached garage. Must be installed and operational at beginning of tenancy. Landlord responsible for providing and installing alarms. Tenant responsible for testing and replacing batteries. Violation is misdemeanor; tenant may also pursue civil remedies.""",
                "category": "habitability",
                "state": "illinois",
                "jurisdiction": "state"
            },
            {
                "section": "Chicago RLTO 5-12-110",
                "title": "Chicago Security Deposit Ordinance",
                "text": """In Chicago, security deposit cannot exceed 1.5 times monthly rent. Landlord must pay interest annually at rate set by city ordinance. Must provide receipt with landlord's name and address. Within 45 days of move-out, must return deposit with itemized statement of deductions and interest accrued. Failure allows tenant to sue for two times deposit plus interest, attorney fees, and court costs. Deductions allowed only for unpaid rent and damage beyond normal wear and tear.""",
                "category": "security_deposit",
                "state": "illinois",
                "jurisdiction": "state"
            }
        ]
    
    def get_washington_laws(self) -> List[Dict]:
        """Washington Revised Code (RCW) 59.18"""
        return [
            {
                "section": "59.18.270",
                "title": "Security Deposit - Return and Deductions",
                "text": """Landlord must return deposit within 30 days after tenant vacates and returns keys. Must provide written itemized statement of basis for retaining any portion. Allowable deductions: unpaid rent, damage beyond normal wear and tear, cleaning costs to restore to move-in condition. If landlord fails to return deposit or provide statement within 30 days, liable for full deposit amount plus actual damages. Normal wear and tear cannot be deducted.""",
                "category": "security_deposit",
                "state": "washington",
                "jurisdiction": "state"
            },
            {
                "section": "59.18.280",
                "title": "Security Deposit - Holding Requirements",
                "text": """No maximum limit on security deposit amount (unusual among states). Deposit must be held in trust and used only for authorized purposes. Landlord need not pay interest unless lease requires it. Upon sale of property, landlord must either transfer deposit to new owner with tenant notice, or return deposit to tenant.""",
                "category": "security_deposit",
                "state": "washington",
                "jurisdiction": "state"
            },
            {
                "section": "59.18.060",
                "title": "Landlord Duties - Habitability",
                "text": """Landlord must: (1) maintain structural components in good repair, (2) keep premises fit for human habitation, (3) keep common areas clean and safe, (4) maintain plumbing, heating, and electrical systems in working order, (5) provide adequate receptacles for garbage, (6) provide locks and furnish keys, and (7) maintain compliance with housing codes. Duty arises at beginning of tenancy and continues throughout. Violations allow tenant remedies.""",
                "category": "habitability",
                "state": "washington",
                "jurisdiction": "state"
            },
            {
                "section": "59.18.070",
                "title": "Tenant Remedies for Landlord Violations",
                "text": """If landlord fails to fulfill duties materially affecting health or safety, tenant may deliver written notice specifying breach. If not remedied within reasonable time (up to 10 days), tenant may: (1) terminate lease with 20 days notice, (2) pursue court remedies, or (3) if repair cost doesn't exceed one month's rent, arrange repair and deduct cost. Tenant may also sue for damages and attorney fees.""",
                "category": "remedies",
                "state": "washington",
                "jurisdiction": "state"
            },
            {
                "section": "59.18.230",
                "title": "Retaliatory Eviction Prohibited",
                "text": """Landlord cannot increase rent, decrease services, terminate tenancy, or threaten to do so in retaliation for tenant: (1) complaining to landlord about violations, (2) complaining to government agency, (3) organizing or joining tenant union, or (4) asserting rights under law. Presumption of retaliation if action within 90 days of protected activity. Landlord must prove legitimate, non-retaliatory reason.""",
                "category": "retaliation",
                "state": "washington",
                "jurisdiction": "state"
            },
            {
                "section": "59.18.200",
                "title": "Termination Notice Requirements",
                "text": """For month-to-month tenancy, landlord must provide 20 days notice to terminate without cause (in Seattle, just cause required or minimum 180 days notice). Tenant must provide 20 days notice. For week-to-week, 7 days notice required. Notice must be in writing. For fixed-term leases, parties bound until end of term unless lease allows early termination.""",
                "category": "termination",
                "state": "washington",
                "jurisdiction": "state"
            },
            {
                "section": "59.18.150",
                "title": "Landlord Entry - Notice Required",
                "text": """Landlord may enter only with 2 days notice (48 hours) for: (1) inspection, (2) making repairs, (3) showing to prospective tenants/buyers. Entry must be at reasonable times. In emergencies, may enter without notice. If tenant unreasonably refuses entry after proper notice, landlord may enter or obtain court order. Landlord cannot abuse right of entry to harass tenant.""",
                "category": "entry_notice",
                "state": "washington",
                "jurisdiction": "state"
            },
            {
                "section": "59.18.290",
                "title": "Unlawful Detainer - Eviction Procedures",
                "text": """To evict, landlord must provide proper notice (14 days for nonpayment of rent, 10 days for lease violation, 20 days for no-cause termination of month-to-month). If tenant doesn't comply, landlord files unlawful detainer action in court. Cannot use self-help eviction - cannot lock out tenant or remove belongings without court order. If landlord violates, tenant may recover possession, actual damages of up to $100 per day, attorney fees.""",
                "category": "eviction",
                "state": "washington",
                "jurisdiction": "state"
            },
            {
                "section": "59.18.365",
                "title": "Domestic Violence Protection - Lease Termination",
                "text": """Victim of domestic violence, sexual assault, stalking, or human trafficking may terminate lease with 20 days written notice. Must provide certification from qualified third party (police, court, attorney, domestic violence advocate). Landlord cannot charge early termination fee. Remaining co-tenants may remain. Landlord may not disclose tenant's status as DV victim except as required by law.""",
                "category": "tenancy_rights",
                "state": "washington",
                "jurisdiction": "state"
            },
            {
                "section": "59.18.283",
                "title": "Last Month's Rent as Security Deposit",
                "text": """If landlord requires prepayment of last month's rent, it must be held in trust and applied to last month's occupancy. Cannot be used for damages - separate security deposit required for that purpose. If tenant terminates early, last month's rent does not cover early termination damages. Landlord must account separately for last month's rent and security deposit.""",
                "category": "security_deposit",
                "state": "washington",
                "jurisdiction": "state"
            }
        ]
    
    def get_massachusetts_laws(self) -> List[Dict]:
        """Massachusetts General Laws Chapter 186"""
        return [
            {
                "section": "186 §15B",
                "title": "Security Deposit Requirements",
                "text": """Security deposit cannot exceed one month's rent. Must be deposited in Massachusetts bank in separate account earning at least 5% interest or held in last month's rent account. Landlord must provide receipt with bank name and account number within 30 days. Landlord must pay tenant 5% interest annually or deduct from rent. At move-in, landlord must provide statement of existing damage (with tenant right to inspect). At move-out, must return deposit with interest and itemized damages within 30 days. Failure to comply allows tenant to recover three times deposit plus attorney fees and costs.""",
                "category": "security_deposit",
                "state": "massachusetts",
                "jurisdiction": "state"
            },
            {
                "section": "186 §14",
                "title": "Termination of Tenancy - Notice Requirements",
                "text": """For tenancy at will or month-to-month, either party must provide written notice equal to rental payment interval (typically 30 days for monthly rent). For tenancy for term of years, no notice required - lease ends at expiration. Notice must be in writing and properly served. Failure to give proper notice may result in holding over and continued tenancy.""",
                "category": "termination",
                "state": "massachusetts",
                "jurisdiction": "state"
            },
            {
                "section": "186 §15D",
                "title": "Security Deposit Deductions - Allowed Uses",
                "text": """Landlord may deduct from security deposit only for: (1) unpaid rent, (2) damage to apartment beyond normal wear and tear, (3) if lease allows, costs of removing tenant's belongings after abandonment, and (4) unpaid tax on rent if lease makes tenant liable. Cannot deduct for normal wear and tear, cleaning fees unless apartment left in unclean condition, or attorney fees in eviction unless court awards them. Must provide itemized list with receipts or estimates for repairs over $50.""",
                "category": "security_deposit",
                "state": "massachusetts",
                "jurisdiction": "state"
            },
            {
                "section": "239 §2A",
                "title": "Retaliation Against Tenant Prohibited",
                "text": """Landlord cannot evict, refuse to renew, increase rent, or decrease services in retaliation for tenant: (1) reporting code violations to authorities, (2) complaining to landlord about violations, (3) organizing or joining tenant organization, or (4) exercising rights under law. Presumption of retaliation if action within 6 months of protected activity. Landlord can rebut by showing legitimate reason. Burden on landlord to prove non-retaliation.""",
                "category": "retaliation",
                "state": "massachusetts",
                "jurisdiction": "state"
            },
            {
                "section": "111 §127L",
                "title": "Sanitary Code - Minimum Standards",
                "text": """State sanitary code requires: (1) weathertight roof, walls, windows, doors, (2) working heating system capable of maintaining 68°F day/64°F night in occupied rooms, (3) working toilet, sink, bathtub/shower with hot and cold running water, (4) adequate lighting and ventilation, (5) safe electrical wiring, (6) proper drainage and sewage disposal, (7) screens on windows from April to October, (8) smoke and carbon monoxide detectors, and (9) freedom from infestation and hazards. Violations render unit uninhabitable and may justify rent withholding.""",
                "category": "habitability",
                "state": "massachusetts",
                "jurisdiction": "state"
            },
            {
                "section": "186 §16",
                "title": "Landlord Entry - Notice and Consent",
                "text": """Landlord has no right to enter except: (1) by agreement in lease, (2) to inspect for damage, make repairs with reasonable notice, or (3) in emergency. If lease is silent, landlord may only enter with consent or in emergency. Generally, 24 hours notice considered reasonable. Entry must be at reasonable times. Landlord cannot abuse right of entry to harass tenant. Unauthorized entry may constitute trespass.""",
                "category": "entry_notice",
                "state": "massachusetts",
                "jurisdiction": "state"
            },
            {
                "section": "239 §8A",
                "title": "Eviction Procedures - Summary Process",
                "text": """To evict, landlord must serve notice to quit (14 days for nonpayment, 7 days for breach, 30 days for no fault). If tenant doesn't vacate, landlord files summary process complaint in court. Court summons tenant to hearing. If landlord prevails, receives execution (eviction order). Sheriff enforces after 10-day appeal period. Self-help eviction (lockout, utility shutoff) is illegal. Tenant can sue for wrongful eviction and recover three months rent or three times damages, attorney fees.""",
                "category": "eviction",
                "state": "massachusetts",
                "jurisdiction": "state"
            },
            {
                "section": "186 §15B(2)(d)",
                "title": "Move-In Inspection Requirement",
                "text": """Within 10 days of taking possession, landlord must provide tenant with written statement of existing damage. Tenant has right to inspect unit and note any disagreements. Both parties should sign statement. This establishes baseline condition. At move-out, only damage beyond what was listed or normal wear and tear can be deducted from deposit. Landlord's failure to provide statement means no deductions allowed except unpaid rent.""",
                "category": "security_deposit",
                "state": "massachusetts",
                "jurisdiction": "state"
            },
            {
                "section": "186 §19",
                "title": "Lead Paint Disclosure Requirements",
                "text": """For properties built before 1978 with child under 6 residing, landlord must: (1) remove or cover all lead paint hazards, (2) provide tenant with notification of compliance, (3) provide pamphlet on lead poisoning prevention. Failure to comply allows tenant to terminate lease, receive damages up to four months rent, and attorney fees. Additionally subject to federal lead disclosure requirements. Violation is serious and can result in significant penalties.""",
                "category": "habitability",
                "state": "massachusetts",
                "jurisdiction": "state"
            },
            {
                "section": "93A",
                "title": "Consumer Protection - Unfair Practices",
                "text": """Chapter 93A prohibits unfair or deceptive acts in trade or commerce, including landlord-tenant relationships. Violations include: charging excessive fees, misrepresenting condition of property, failing to return deposit unlawfully, or retaliating against tenant. Tenant may make demand letter for damages. If landlord doesn't respond within 30 days, tenant can sue for double or triple damages plus attorney fees. Powerful tenant remedy for landlord misconduct.""",
                "category": "remedies",
                "state": "massachusetts",
                "jurisdiction": "state"
            }
        ]
    
    def get_federal_laws(self) -> List[Dict]:
        """Federal tenant protection laws"""
        return [
            {
                "section": "Fair Housing Act Title VIII",
                "title": "Prohibition of Housing Discrimination",
                "text": """Federal law prohibits housing discrimination based on race, color, national origin, religion, sex, familial status (families with children under 18), or disability. Applies to rental housing, sales, lending, and homeowner's insurance. Landlords cannot: refuse to rent, set different terms/conditions, advertise discriminatory preferences, falsely deny availability, or harass tenants. Includes prohibition on sexual harassment. Complaints filed with HUD. Violations can result in fines up to $100,000+ and damages to victim.""",
                "category": "discrimination",
                "state": "federal",
                "jurisdiction": "federal"
            },
            {
                "section": "SCRA Section 305",
                "title": "Servicemembers Civil Relief Act - Lease Termination",
                "text": """Active duty military members can terminate residential leases if: (1) lease entered before military service began and member receives orders for permanent change of station or deployment of 90+ days, OR (2) lease entered during military service and member receives PCS orders or deployment 90+ days. Must provide written notice and copy of orders. Termination effective 30 days after next rent due date following notice. Landlord cannot charge early termination fee. Applies to servicemembers and dependents.""",
                "category": "termination",
                "state": "federal",
                "jurisdiction": "federal"
            },
            {
                "section": "ADA Title III",
                "title": "Americans with Disabilities Act - Reasonable Accommodations",
                "text": """Landlords must make reasonable accommodations for tenants with disabilities. Must allow reasonable modifications at tenant's expense (tenant may be required to restore to original at move-out for common areas). Cannot charge pet deposit or pet rent for service animals or emotional support animals (but can charge for actual damage caused by animal). Must engage in interactive process with tenant to determine what accommodations are reasonable. Failure to accommodate is discrimination under Fair Housing Act.""",
                "category": "discrimination",
                "state": "federal",
                "jurisdiction": "federal"
            },
            {
                "section": "42 USC 4852d",
                "title": "Lead-Based Paint Disclosure Requirement",
                "text": """For housing built before 1978, landlord must: (1) disclose known lead-based paint and hazards, (2) provide EPA-approved pamphlet 'Protect Your Family from Lead in Your Home', (3) include specific warning language in lease, (4) provide any records or reports on lead paint, and (5) give tenant 10-day period to conduct lead inspection before lease becomes binding. Landlord and tenant must sign disclosure form. Failure to comply can result in penalties up to $16,000+ per violation, plus tenant can sue for damages.""",
                "category": "habitability",
                "state": "federal",
                "jurisdiction": "federal"
            },
            {
                "section": "FHA Familial Status Protection",
                "title": "Fair Housing - Families with Children",
                "text": """Landlords cannot refuse to rent to families with children (with limited exception for senior housing). Cannot set different terms (higher deposit, rent, restricting where children can play). Cannot advertise 'adults only' or 'no children'. Cannot segregate families with children to certain buildings or floors. Familial status includes pregnant women and those in process of obtaining custody. Violations subject to HUD complaints and civil liability.""",
                "category": "discrimination",
                "state": "federal",
                "jurisdiction": "federal"
            },
            {
                "section": "Violence Against Women Act (VAWA)",
                "title": "Protection for Domestic Violence Victims",
                "text": """In federally subsidized housing, landlords cannot evict tenant who is victim of domestic violence, dating violence, sexual assault, or stalking based on acts or threats by the perpetrator. Victim can request to transfer to different unit. Landlord may bifurcate lease to remove perpetrator while allowing victim to remain. Does not apply to private, non-subsidized housing (but many states have similar protections). Tenant may need to provide certification of abuse.""",
                "category": "tenancy_rights",
                "state": "federal",
                "jurisdiction": "federal"
            },
            {
                "section": "ECOA - Equal Credit Opportunity Act",
                "title": "Fair Screening and Application Process",
                "text": """Landlords cannot discriminate in tenant screening based on race, color, religion, national origin, sex, marital status, age, or receipt of public assistance. Must apply same screening criteria to all applicants. If denying application based on credit report or background check, must provide adverse action notice with name of screening company and applicant's right to dispute. Screening fees must be reasonable and based on actual costs.""",
                "category": "discrimination",
                "state": "federal",
                "jurisdiction": "federal"
            },
            {
                "section": "Fair Credit Reporting Act",
                "title": "Tenant Screening and Background Checks",
                "text": """Landlords using tenant screening services must: (1) get written consent from applicant, (2) provide notice if taking adverse action based on report, (3) inform applicant of right to dispute inaccurate information, and (4) dispose of screening reports securely. Cannot consider arrests without convictions in most cases. Some states further limit use of criminal history. Applicant can request free copy of report if denied. Violations can result in damages and FTC penalties.""",
                "category": "screening",
                "state": "federal",
                "jurisdiction": "federal"
            }
        ]
    
    def build_all_laws(self) -> Dict[str, List[Dict]]:
        """Build complete multi-state database"""
        
        self.laws_by_state = {
            "california": self.get_california_laws(),
            "new_york": self.get_new_york_laws(),
            "texas": self.get_texas_laws(),
            "florida": self.get_florida_laws(),
            "illinois": self.get_illinois_laws(),
            "washington": self.get_washington_laws(),
            "massachusetts": self.get_massachusetts_laws(),
        }
        
        self.federal_laws = self.get_federal_laws()
        
        return self.laws_by_state
    
    def get_laws_for_state(self, state: str) -> List[Dict]:
        """
        Get laws for specific state + federal laws.
        
        Args:
            state: State name (e.g., "california", "new york")
            
        Returns:
            Combined list of state laws + federal laws
        """
        
        state = state.lower().replace(" ", "_")
        
        # Build database if not already built
        if not self.laws_by_state:
            self.build_all_laws()
        
        if state not in self.laws_by_state:
            raise ValueError(
                f"State '{state}' not yet supported. "
                f"Supported states: {', '.join(self.SUPPORTED_STATES)}"
            )
        
        # Combine state laws + federal laws
        state_laws = self.laws_by_state.get(state, [])
        combined = state_laws + self.federal_laws
        
        return combined
    
    def save_to_json(self, output_dir: str = "data/laws"):
        """Save all laws to JSON files"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Build all laws
        self.build_all_laws()
        
        # Save each state separately
        for state, laws in self.laws_by_state.items():
            filepath = f"{output_dir}/{state}_laws.json"
            with open(filepath, "w") as f:
                json.dump(laws, f, indent=2)
            print(f"✓ Saved {len(laws)} laws for {state}")
        
        # Save federal laws
        filepath = f"{output_dir}/federal_laws.json"
        with open(filepath, "w") as f:
            json.dump(self.federal_laws, f, indent=2)
        print(f"✓ Saved {len(self.federal_laws)} federal laws")
        
        # Save combined database
        all_laws = {
            "states": self.laws_by_state,
            "federal": self.federal_laws,
            "supported_states": self.SUPPORTED_STATES
        }
        
        filepath = f"{output_dir}/all_laws_database.json"
        with open(filepath, "w") as f:
            json.dump(all_laws, f, indent=2)
        print(f"✓ Saved complete multi-state database")
        
        # Print summary
        print(f"\n{'='*60}")
        print("MULTI-STATE LAW DATABASE SUMMARY")
        print(f"{'='*60}")
        print(f"Total states: {len(self.laws_by_state)}")
        print(f"Federal laws: {len(self.federal_laws)}")
        
        total_sections = sum(len(laws) for laws in self.laws_by_state.values())
        print(f"Total state law sections: {total_sections}")
        print(f"Grand total: {total_sections + len(self.federal_laws)} sections")
        
        print(f"\nState breakdown:")
        for state, laws in sorted(self.laws_by_state.items()):
            print(f"  {state.title()}: {len(laws)} sections")

# Build database
if __name__ == "__main__":
    db = StateLawDatabase()
    db.save_to_json()