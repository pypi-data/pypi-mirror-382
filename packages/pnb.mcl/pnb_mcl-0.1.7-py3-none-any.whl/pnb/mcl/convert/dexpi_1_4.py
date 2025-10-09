import datetime


from pnb.mcl.metamodel import standard as metamodel
    
    
def iter_spec(obj):
    
    for member in obj.ownedMembers:
        yield member
        if isinstance(member, metamodel.Namespace):
            yield from iter_spec(member)
            
            
class DexpiPlant_1_4_to_2_0:
    
    def __init__(self, model_set, plant):

        self.type_by_name = {}
        self.model_set = model_set

        for model in model_set:
            for element in iter_spec(model):
                if isinstance(element, metamodel.Type):
                    name = element.name
                    
                    if name == 'Symbol':
                        continue
                    
                    if name in self.type_by_name:
                        print(element, self.type_by_name[name])
                        ERROR
                    else:
                        self.type_by_name[name] = element
                        
                        
        self.old_by_new = {}
        self.new_by_old = {}
        
        self.result = self.convert_obj(plant)
        
        for obj in self.old_by_new:
            self.add_references(obj)
            
            

    def convert_obj(self, value):
        

        type_name = value.type.name
        
        is_thermowell = False
        
        if type_name.startswith('Custom'):
            is_custom = True
            custom_type_name = value.TypeName
            assert custom_type_name, value
            
            
            if custom_type_name == 'Thermowell':
                new_type = self.type_by_name.get('Sensorwell')
                is_thermowell = True
                
            else:
                new_type = self.type_by_name.get(custom_type_name)
            
            
            
            if not new_type:
                print('SKIP CUSTOM TYPE NAME', custom_type_name)
                TODO
                return
            # TODO: check uri
        else:
            is_custom = False
            if type_name.endswith('Shape'):
                new_type_name = 'Shape'
            else:
                new_type_name = {
                    'DexpiModel': 'EngineeringModel',
                    'ConceptualModel': 'PlantModel',
                    'MetaData': 'PlantMetaData'}.get(type_name, type_name)
            new_type = self.type_by_name[new_type_name]

        new_value = new_type()
        
        if is_thermowell:
            new_value.SensorwellTypeRepresentation = 'Thermowell'
            
        
        assert not new_type.isAbstract, new_type
        
        for prop, prop_values in value._attribute_values_.items():
            
            if is_custom:
                if prop.name in ['TypeName', 'TypeURI']:
                    continue
                
            if prop.name == 'CustomAttributes':
                continue # TODO

            if isinstance(prop, metamodel.ReferenceProperty):
                continue
            
            if prop.name == 'NominalCapacity_Volume_':
                new_prop = new_type.attributes['NominalCapacityVolume']
            else:
                new_prop = new_type.attributes.get(prop.name)
                if not new_prop:
                    print('TODO', prop, value, new_value)
                    print(list(new_value.type.allSuperTypes))
                    ji
                    continue
            
            if isinstance(prop, metamodel.DataProperty):
                new_prop_values = [self.convert_data(prop_value) for prop_value in prop_values]
            else:
                new_prop_values = [value for value in [self.convert_obj(prop_value) for prop_value in prop_values]
                                   if value is not None]
            new_prop._set_values_(new_value, new_prop_values)
            
        self.old_by_new[new_value] = value
        self.new_by_old[value] = new_value
            
            
        for co in getattr(value, 'CustomAttributes', []):
            
            assert co.type.name == 'CustomStringAttribute'
            name = co.AttributeName
            
            if name.endswith('AssignmentClass'):
                name = name[:-len('AssignmentClass')]
            
            
            prop = new_type.attributes.get(name)
            
            #print('################', type_name, new_type, name, prop)
            #print('++', new_type.attributes)
            if prop:
                
                
                value = co.Value
                
                if repr(value) == "<SingletonValue 'dexpi.DataTypes.NULL_STRING'>":
                    value = self.model_set['Builtin'].search_unique('Undefined')()
                else:
                    assert isinstance(value, str)
                    
                if name in ['HeatTraceRequired', 'IsVirtual', 'IsVirtualMount']:
                    value = {'N': False, 'Y': True, 'false': False, 'true': True}[value]
                    
                if name in ['LineIdBreak']:
                    value = {'LineIdBreak': True}[value]
                if name in ['AreaBreak']:
                    value = {'AreaBreak': True}[value]
                
                prop._set_(new_value, value)

            else:
                if name in ['TagSuffix']:
                    print('########################', new_type.name)
                    hu
                    assert new_type.name in ['ClampOn', 'CoriolisMassFlowMeter',
                                            #  'Sensorwell'
                                              ], new_type.name
                    # add to inlinemeasueringelement, sensorwell
                    
                elif name in ['NominalDiameter']:
                    assert new_type.name in ['CheckValve'], new_type.name

                elif name == 'ObjectDisplayName' and new_type.name == 'ProcessInstrumentationFunction':
                    pass
                    # ignore
                else:
                    TODO
                

            

            
            
        return new_value
    
    
    def convert_data(self, value):
        if isinstance(value, (str, int, float, datetime.datetime)):
            return value
        elif isinstance(value, metamodel.SingletonValue):
            assert value.name.startswith('NULL')
            return metamodel.BUILTIN.Undefined()
        elif isinstance(value, metamodel.AggregatedDataValue):
            
            if sorted(a.name for a in value.type.attributes) == ['Unit', 'Value']:
                new_type = self.type_by_name['PhysicalQuantity']
            else:
                type_name = value.type.name
                new_type_name = {}.get(type_name, type_name)
                new_type = self.type_by_name[new_type_name]
                
            new_value = new_type()


            for prop, prop_values in value._attribute_values_.items():
                
                if prop.name == 'NominalCapacity_Volume_':
                    new_prop = new_type.attributes['NominalCapacityVolume']
                else:
                

                    new_prop = new_type.attributes.get(prop.name)
            
                    if not new_prop:
                        print('TODO data prop', prop)
                        TODO
                        continue
                
                assert isinstance(prop, metamodel.DataProperty)
                new_prop_values = [self.convert_data(prop_value) for prop_value in prop_values]
                new_prop._set_values_(new_value, new_prop_values)


            return new_value

        elif isinstance(value, metamodel.EnumerationLiteral):
            old_enum_name = value.owner.name
            new_enum = self.type_by_name[old_enum_name]
            assert isinstance(new_enum, metamodel.Enumeration)
            new_value = getattr(new_enum, value.name)
            return new_value
            
        else:
            raise TypeError(repr(value), type(value), value)
    
    
    def add_references(self, new_obj):
        new_type = new_obj.type
        old_obj = self.old_by_new[new_obj]
        
        for old_prop, old_values in old_obj._attribute_values_.items():
            
            if not isinstance(old_prop, metamodel.ReferenceProperty):
                continue
            
            
            new_prop = new_type.attributes.get(old_prop.name)
            if not new_prop:
                print('TODO', old_prop)
                TODO
                continue
            new_prop._set_values_(new_obj, 
                                  
                          [value for value in         
                                  
                                  
                                  
                                  [self.new_by_old.get(old) for old in old_values]
                            if value is not None])

        
    