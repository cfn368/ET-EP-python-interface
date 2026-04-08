
# ==================== ==================== ==================== ====================
# Full labels dictionary — keys are exact EnergyPLAN output column names
labels = {

    # 1a. electricity demand
    'Electr._Demand':       'Electricity demand',
    'Elec.dem_Cooling':     'Electricity demand for cooling',
    'Flexible_Electr.':     'Flexible electricity demand',
    'Fixed_Exp/Imp':        'Fixed exchange',
    'DH_Demand':            'District heating demand',
    'Stabil._Load':         'Stabilisation load',

    # 1b. renewable electricity generation
    'Wind_Electr.':         'Onshore wind',
    'Offshore_Electr.':     'Offshore wind',
    'PV_Electr.':           'Solar PV',
    'River_Electr.':        'Run-of-river hydro',
    'Tidal_Electr.':        'Tidal',
    'Wave_Electr.':         'Wave',
    'CSP_Electr.':          'CSP (electricity)',
    'CSP2_Electr.':         'CSP2 (electricity)',
    'CSP2_Storage':         'CSP2 storage',
    'CSP2_loss':            'CSP2 losses',
    'Hydro_Electr.':        'Hydro (electricity)',
    'Hydro_pump':           'Hydro pump',
    'Hydro_storage':        'Hydro storage',
    'Hydro_Wat-Sup':        'Hydro water supply',
    'Hydro_Wat-Loss':       'Hydro water loss',
    'Geother._Electr.':     'Geothermal electricity',

    # 1c. thermal & CHP electricity
    'PP_Electr.':           'Power plant',
    'PP2_Electr.':          'Peak load plant',
    'Nuclear_Electr.':      'Nuclear',
    'CHP_Electr.':          'CHP electricity',
    'CSHP_Electr.':         'CSHP electricity',
    'HP_Electr.':           'Heat pump electricity',

    # 1d. electricity storage
    'Charge_Electr.':       'Electricity storage charging',
    'Discharge_Electr.':    'Electricity storage discharging',
    'Store_Storage':        'Electricity storage content',
    'Charge2_Electr.':      'Electricity storage 2 charging',
    'Discharge2_Electr.':   'Electricity storage 2 discharging',
    'Store2_Storage':       'Electricity storage 2 content',
    'Storage_Content':      'Storage content',

    # 1e. V2G
    'V2G_Demand':           'V2G demand',
    'V2G_Charge':           'V2G charging',
    'V2G_Discha.':          'V2G discharging',
    'V2G_Storage':          'V2G storage',

    # 1f. electrolysis & power-to-X
    'H2_Electr.':           'Electrolysis',
    'CO2Hydro_Electr.':     'CO2 hydrogenation electricity',
    'NH3Hydro_Electr.':     'NH3 hydrogenation electricity',
    'ELT 2_Electr.':        'Electrolysis 2 electricity',
    'ELT 3_Electr.':        'Electrolysis 3 electricity',
    'ELT 2 H2_ELT 2':       'Electrolysis 2 H2 output',
    'ELT 3 H2_ELT 3':       'Electrolysis 3 H2 output',

    # 1g. rock/thermal storage
    'Rock in_Electr.':      'Rock storage charging electricity',
    'Rock out_Steam':       'Rock storage steam output',
    'Rock str_Storage':     'Rock storage content',

    # 1h. import / export / exchange
    'Import_Electr.':       'Electricity imports',
    'Export_Electr.':       'Electricity exports',
    'CEEP_Electr.':         'Critical excess electricity',
    'EEEP_Electr.':         'Export excess electricity',

    # 1i. market prices & payments
    'ExMarket_Prices':      'Export market price (EUR/MWh)',
    'ExMarket_Prod':        'Export market production',
    'System_Prices':        'System price (EUR/MWh)',
    'InMarket_Prices':      'Market electricity price (EUR/MWh)',
    'Btl-neck_Prices':      'Bottleneck price (EUR/MWh)',
    'Import_Payment':       'Import payment (MEUR)',
    'Export_Payment':       'Export payment (MEUR)',
    'Blt-neck_Payment':     'Bottleneck payment (MEUR)',
    'Add-exp_Payment':      'Additional export payment (MEUR)',

    # 2a. heat group 1 (DH)
    'Solar_Heat':           'Solar thermal heat',
    'CSHP 1_Heat':          'CSHP heat (group 1)',
    'Waste 1_Heat':         'Waste heat (group 1)',
    'Boiler 1_Heat':        'Boiler heat (group 1)',
    'Solar 1_Heat':         'Solar heat (group 1)',
    'Sol1 Str_Heat':        'Solar storage (group 1)',

    # 2b. heat group 2 (DH)
    'CSHP 2_Heat':          'CSHP heat (group 2)',
    'Waste 2_Heat':         'Waste heat (group 2)',
    'Geoth 2_Heat':         'Geothermal heat (group 2)',
    'Geoth 2_Steam':        'Geothermal steam (group 2)',
    'Geoth 2_Storage':      'Geothermal storage (group 2)',
    'CHP 2_Heat':           'CHP heat (group 2)',
    'HP 2_Heat':            'Heat pump heat (group 2)',
    'Boiler 2_Heat':        'Boiler heat (group 2)',
    'EH 2_Heat':            'Electric heating (group 2)',
    'ELT 2_Heat':           'Electrolysis heat (group 2)',
    'Solar2_Heat':          'Solar heat (group 2)',
    'Sol2 Str_Heat':        'Solar storage (group 2)',
    'Storage2_Heat':        'Thermal storage (group 2)',
    'Balance2_Heat':        'Heat balance (group 2)',

    # 2c. heat group 3 (individual)
    'CSHP 3_Heat':          'CSHP heat (group 3)',
    'Waste 3_Heat':         'Waste heat (group 3)',
    'Geoth 3_Heat':         'Geothermal heat (group 3)',
    'Geoth 3_Steam':        'Geothermal steam (group 3)',
    'Geoth 3_Storage':      'Geothermal storage (group 3)',
    'CHP 3_Heat':           'CHP heat (group 3)',
    'HP 3_Heat':            'Heat pump heat (group 3)',
    'Boiler 3_Heat':        'Boiler heat (group 3)',
    'EH 3_Heat':            'Electric heating (group 3)',
    'ELT 3_Heat':           'Electrolysis heat (group 3)',
    'Solar3_Heat':          'Solar heat (group 3)',
    'Sol3 Str_Heat':        'Solar storage (group 3)',
    'Storage3_Heat':        'Thermal storage (group 3)',
    'Balance3_Heat':        'Heat balance (group 3)',

    # 2d. household heat
    'HH Dem._Heat':         'HH heat demand',
    'HH CHP+HP_Heat':       'HH CHP+HP heat',
    'HH Boil._Heat':        'HH boiler heat',
    'HH Solar_Heat':        'HH solar heat',
    'HH Store_Heat':        'HH thermal storage',
    'HH Balan_Heat':        'HH heat balance',

    # 2e. household electricity
    'HH-CHP_Electr.':       'HH CHP electricity',
    'HH-HP_Electr.':        'HH heat pump electricity',
    'HH-HP/EB_Electr.':     'HH HP/electric boiler electricity',
    'HH-EB_Electr.':        'HH electric boiler electricity',
    'HH-H2_Electr.':        'HH hydrogen electricity',
    'HH-H2_Storage':        'HH hydrogen storage',
    'HH-H2_Prices':         'HH hydrogen price',

    # 3. fuel demand aggregates
    'Boilers':              'Boiler fuel demand',
    'CHP2+3':               'CHP 2+3 fuel demand',
    'PP_CAES':              'PP/CAES fuel demand',
    'Indi-_vidual':         'Individual heating fuel demand',
    'Transp.':              'Transport fuel demand',
    'Indust._Various':      'Industry fuel demand',
    'Demand_Sum':           'Total fuel demand',

    # 4. gas & fuels
    'Biogas':               'Biogas',
    'Syngas':               'Synthetic gas',
    'CO2HyGas':             'CO2 hydrogenation gas',
    'SynHyGas':             'Synthetic hydrogen gas',
    'SynFuel':              'Synthetic fuel',
    'CO2Hydro_liq.fuel':    'CO2 hydrogenation liquid fuel',
    'NH3Hydro_Ammonia':     'Ammonia production',
    'Storage':              'Gas storage',
    'Sum':                  'Gas sum',
    'Import_Gas':           'Gas imports',
    'Export_Gas':           'Gas exports',

    # 5. hydrogen
    'H2_demand':            'Hydrogen demand',
    'H2_prod.':             'Hydrogen production',
    'H2_Storage':           'Hydrogen storage',
    'H2_import':            'Hydrogen imports',
    'H2_export':            'Hydrogen exports',
    'H2_balance':           'Hydrogen balance',
    'Ammonia_Storage':      'Ammonia storage',

    # 6. water & desalination
    'FreshW_Demand':        'Fresh water demand',
    'FreshW_Storage':       'Fresh water storage',
    'SaltW_Demand':         'Salt water demand',
    'Brine_Prod.':          'Brine production',
    'Brine_Storage':        'Brine storage',
    'Desal.Pl_Electr.':     'Desalination plant electricity',
    'FWPump_Electr.':       'Fresh water pump electricity',
    'Turbine_Electr.':      'Turbine electricity',
    'Pump_Electr.':         'Pump electricity',

    # 7. cooling
    'CoolGr1_Demand':       'Cooling demand (group 1)',
    'CoolGr2_Demand':       'Cooling demand (group 2)',
    'CoolGr3_Demand':       'Cooling demand (group 3)',
    'Cool-El_Demand':       'Cooling electricity demand',
    'CoolGr1_Natural':      'Natural cooling (group 1)',
    'CoolGr2_Natural':      'Natural cooling (group 2)',
    'CoolGr3_Natural':      'Natural cooling (group 3)',
    'Cooling_DHgr1':        'DH cooling (group 1)',
    'Cooling_DHgr2':        'DH cooling (group 2)',
    'Cooling_DHgr3':        'DH cooling (group 3)',
    'Cooling_Electr.':      'Electric cooling',
}
