from collections import namedtuple
from dataclasses import dataclass
import warnings

import typing as T

from lxml import etree
from pnb.mcl.utils import SYMBOL_PATTERN, check_is_symbol


class XmlNamespace(str):
    def __getattr__(self, fragment):
        return f'{{{self}}}{fragment}'

XMI = XmlNamespace('http://schema.omg.org/spec/XMI/2.1')
NAMESPACES = {'xmi': XMI}



TypeInfo = namedtuple('TypeInfo', ['xmi_id', 'super_type_xmi_ids', 'xmi_element'])
ObjectInfo = namedtuple('ObjectInfo', ['xmi_id', 'xmi_element'])


def sorted_by_dependency(type_infos):
    """Iterate over type_infos such that each type_info precedes its sub types."""
    handled_xmi_ids = set()
    while type_infos:
        infos_to_handle = []
        progress_made = False
        for info in type_infos:
            if info.super_type_xmi_ids.issubset(handled_xmi_ids):
                progress_made = True
                handled_xmi_ids.add(info.xmi_id)
                yield info
            else:
                infos_to_handle.append(info)
        assert progress_made, 'no progress made (missing ids? cycle?)'
        type_infos = infos_to_handle


class XmiReader:
    
    def __init__(self, source, meta_model=None, check_primitive_generalizations=False):
        self.check_primitive_generalizations = check_primitive_generalizations
        if not meta_model:
            from pnb.mcl.metamodel import standard as meta_model
        self.meta_model = meta_model
        
        
        self.model_element_by_xmi_id = {}
        self.item_by_xmi_id = {}
        
        root = source[0]
        
        self._build_packaged_elements(root)

        
        
        
      
        
        self.package = self._build_package(source[0], self.meta_model.Model)
        
        self.type_info_by_id = {}
        

        
    def _get_type_infos(self, root_element):
        type_infos = []
        for xmi_element_tag in ['Class', 'DataType', 'Enumeration', 'PrimitiveType']:
            for xmi_element in root_element.xpath(
                    f'//*[@xmi:type="uml:{xmi_element_tag}"]', namespaces=NAMESPACES):
                xmi_id = xmi_element.attrib[XMI.id]
                super_type_xmi_ids = set(xmi_element.xpath(
                    f'generalization[@xmi:type="uml:Generalization"]/@general',
                    namespaces=NAMESPACES))
                type_infos.append(TypeInfo(xmi_id, super_type_xmi_ids, xmi_element))
                
                
        if self.check_primitive_generalizations:
            info_by_name = {info.xmi_element.attrib['name']: info for info in type_infos}

            
            for info in type_infos:
                if info.xmi_element.attrib[XMI.type] == 'uml:PrimitiveType':
                    name = info.xmi_element.attrib['name']
                    super_type_name = 'Nullable' + name
                    if super_type_name in info_by_name:
                        super_type_xmi_id = info_by_name[super_type_name].xmi_id
                        info.super_type_xmi_ids.add(super_type_xmi_id)
                      #  print("--- Add nullable supertype to ", name)
                     #   print(info_by_name['String'])

                    else:
                        
                        pass
                       # print("--- No nullable supertype for ", name)

  
        return list(sorted_by_dependency(type_infos))
    
    
      
    def _build_type(self, type_info):
        
        xmi_element = type_info.xmi_element
        xmi_type = xmi_element.attrib[XMI.type]
        name = xmi_element.attrib['name']
        is_abstract = xmi_element.get('isAbstract') == 'true'
        super_types = [self.item_by_xmi_id[xmi_id] for xmi_id in type_info.super_type_xmi_ids]

        match xmi_type:
            case 'uml:Class':
                if is_abstract:
                    meta_type = self.meta_model.AbstractClass
                else:
                    meta_type = self.meta_model.ConcreteClass
            case 'uml:DataType':
                if xmi_element.xpath('ownedAttribute'):
                    assert not is_abstract
                    meta_type = self.meta_model.AggregatedDataType
                else:
                    if is_abstract:
                        meta_type = self.meta_model.AbstractDataType
                    else:
                        # TODO: check instances element.xpath('//packagedElement[classifier="{type_id}"]')
                        meta_type = self.meta_model.SingletonType
            case 'uml:PrimitiveType':
                
                prim_prefix = 'Primitive'
                if name.startswith(prim_prefix):
                    name = name[len(prim_prefix):]

                
                if 1: # BUILTIN_PRIMS
                    
                    
                    type_name = name+'Type'
                    
                    type_name = {
                        'AnyURIType': 'StringType',
                        'IntegerType': 'IntegerType',
                        'UnsignedByteType': 'IntegerType'}.get(type_name, type_name)
                    
                    meta_type = getattr(self.meta_model, type_name)
                    
                    
                    
                    
                else:
                
                
                
                    # TODO: super types of primitives -> Union

                    if name == 'Integer':
                        name = 'Int'
                    type_ = getattr(self.meta_model, name)
                    self.item_by_xmi_id[type_info.xmi_id] = type_
                    return
            case 'uml:Enumeration':
                meta_type = self.meta_model.Enumeration
            case _:
                raise Exception(xmi_type)

            
        assert type_info.xmi_id not in self.item_by_xmi_id
        self.item_by_xmi_id[type_info.xmi_id] = meta_type(name, super_types)
        

        return
            
            
        type_ = type_class(name, (self.model_element_by_id[id_] for id_ in superType_ids))
        if type_id in self.model_element_by_id:
            ERROR
        self.model_element_by_id[type_id] = type_
        
        
        

        
        
    def _build_packaged_elements(self, root_element):

        type_infos = self._get_type_infos(root_element)
        for info in type_infos:
            self._build_type(info)
        

        opp_prop_by_prop_id = {}
        for association_element in root_element.xpath(f'//*[@xmi:type="uml:Association"]', namespaces=NAMESPACES):
            prop_ids = association_element.attrib['memberEnd'].split()
            props = association_element.xpath(f'*[@xmi:type="uml:Property"]', namespaces=NAMESPACES)
            assert len(props) == 1
            assert props[0].attrib[XMI.id] == prop_ids[1]
            opp_prop_by_prop_id[prop_ids[0]] = props[0]

        for info in type_infos:
            type_id, superType_ids, type_element = info

            
            for oa in type_element:

                if oa.tag != 'ownedAttribute':
                    continue
                
                prop_type_id = oa.attrib.get('type')
                if not prop_type_id:
                    continue # TODO, e.g. untyped value of CustomAttr
                
                type_ = self.item_by_xmi_id.get(oa.attrib['type'])
                if not type_:
                    continue # TODO
                

                aggregation = oa.attrib.get('aggregation')
                assert aggregation in ('none', 'composite', None)
                if not aggregation:
                    aggregation = 'none'
                    
                
                
                if aggregation == 'composite':
                    assert isinstance(type_, self.meta_model.Class)
                    
                    
                    name = oa.attrib['name']
                    
                    
                    isOrdered = oa.attrib.get('isOrdered')
                    
                    
                    if isOrdered is None:
                        isOrdered=False
                    elif isOrdered == 'true':
                        isOrdered = True
                    else:
                        raise Exception(isOrdered)
                    
                    lowerElements = oa.xpath('lowerValue')
                    if lowerElements:
                        assert len(lowerElements) == 1
                        lowerElement = lowerElements[0]
                        lower = lowerElement.attrib.get('value')
                        if lower is None:
                            lower = 0
                        else:
                            raise Exception(lower)
                    else:
                        lower = 1
                        
                    upperElements = oa.xpath('upperValue')
                    if upperElements:
                        assert len(upperElements) == 1
                        upperElement = upperElements[0]
                        upper = upperElement.attrib.get('value')
                        if upper is None:
                            raise Exception(upper)
                        elif upper == '*':
                            upper = None
                        else:
                            raise Exception(upper)
                        
                        
                    else:
                        upper = 1
                    
               #     print(name, lower, upper, type)
                    
                    
                    self.item_by_xmi_id[type_id].ownedAttributes.add(
                        self.meta_model.CompositionProperty(name, type_, lower, upper, isOrdered))
                    
                elif isinstance(type_, self.meta_model.Class):
                    

                    name = oa.attrib['name']
                    
                    
                    isOrdered = oa.attrib.get('isOrdered')
                    
                    if isOrdered is None:
                        isOrdered=False
                    elif isOrdered == 'true':
                        isOrdered = True
                    else:
                        raise Exception(isOrdered)
                    
                    
                    isUnique = oa.attrib.get('isUnique')
                    
                    if isUnique is None:
                        isUnique=False
                    elif isUnique == 'true':
                        isUnique = True
                    else:
                        raise Exception(isUnique)
                    
                    lowerElements = oa.xpath('lowerValue')
                    if lowerElements:
                        assert len(lowerElements) == 1
                        lowerElement = lowerElements[0]
                        lower = lowerElement.attrib.get('value')
                        if lower is None:
                            lower = 0
                        else:
                            raise Exception(lower)
                    else:
                        lower = 1

                    upperElements = oa.xpath('upperValue')
                    if upperElements:
                        assert len(upperElements) == 1
                        upperElement = upperElements[0]
                        upper = upperElement.attrib.get('value')
                        if upper is None:
                            raise Exception(upper)
                        elif upper == '*':
                            upper = None
                        else:
                            raise Exception(upper)
                    else:
                        upper = 1
                        
                    opp_propElement = opp_prop_by_prop_id[oa.attrib[XMI.id]]
                    oppLowerElements = opp_propElement.xpath('lowerValue')
                    if oppLowerElements:
                        assert len(oppLowerElements) == 1
                        oppLowerElement = oppLowerElements[0]
                        oppLower = oppLowerElement.attrib.get('value')
                        if oppLower is None:
                            oppLower = 0
                        else:
                            oppLower = int(oppLower)
                    else:
                        oppLower = 1
                        
                    oppUpperElements = opp_propElement.xpath('upperValue')
                    if oppUpperElements:
                        assert len(oppUpperElements) == 1
                        oppUpperElement = oppUpperElements[0]
                        oppUpper = oppUpperElement.attrib.get('value')
                        if oppUpper is None:
                            raise Exception(oppUpper)
                        elif oppUpper == '*':
                            oppUpper = None
                        else:
                            oppUpper = int(oppUpper)
                    else:
                        oppUpper = 1
                        

                    self.item_by_xmi_id[type_id].ownedAttributes.add(
                        self.meta_model.ReferenceProperty(name, type_, lower, upper, isOrdered, isUnique, oppLower, oppUpper))
         
                else:

                    name = oa.attrib['name']
                    
                    
                    isOrdered = oa.attrib.get('isOrdered')
                    
                    if isOrdered is None:
                        isOrdered=False
                    elif isOrdered == 'true':
                        isOrdered = True
                    else:
                        raise Exception(isOrdered)

                    isUnique = oa.attrib.get('isUnique')
                    
                    if isUnique is None:
                        isUnique=False
                    elif isUnique == 'true':
                        isUnique = True
                    else:
                        isUnique = False
                    
                    lowerElements = oa.xpath('lowerValue')
                    if lowerElements:
                        assert len(lowerElements) == 1
                        lowerElement = lowerElements[0]
                        lower = lowerElement.attrib.get('value')
                        if lower is None:
                            lower = 0
                        else:
                            lower = int(lower)
                    else:
                        lower = 1
                        
                    upperElements = oa.xpath('upperValue')
                    if upperElements:
                        assert len(upperElements) == 1
                        upperElement = upperElements[0]
                        upper = upperElement.attrib.get('value')
                        if upper is None:
                            raise Exception(upper)
                        elif upper == '*':
                            upper = None
                        else:
                            raise Exception(upper)
                    else:
                        upper = 1

                        
                    name = self.fix_name(name, 'DataProperty')

                    self.item_by_xmi_id[type_id].ownedAttributes.add(
                        self.meta_model.DataProperty(name, type_, lower, upper, isOrdered, isUnique))

            
            for el in type_element:

                if el.tag != 'ownedLiteral':
                    continue
                name = el.attrib['name']
                
                name = self.fix_name(name, 'EnumerationLiteral')
                
                self.meta_model.EnumerationLiteral(name, self.item_by_xmi_id[type_id])

        
        
        self._build_objects(root_element)
        
        
        
    def _get_object_infos(self, root_element):
        object_infos = []
        for xmi_element_tag in ['InstanceSpecification']:
            for xmi_element in root_element.xpath(
                    f'//*[@xmi:type="uml:{xmi_element_tag}"]', namespaces=NAMESPACES):
                xmi_id = xmi_element.attrib[XMI.id]
                object_infos.append(ObjectInfo(xmi_id, xmi_element))
        return object_infos
    
    
    def _build_object(self, object_info):
        
        xmi_element = object_info.xmi_element
        assert xmi_element.attrib[XMI.type] == 'uml:InstanceSpecification'
        name = xmi_element.attrib['name']
        classifier_xmi_id = xmi_element.attrib['classifier']
        classifier = self.item_by_xmi_id.get(classifier_xmi_id)
        assert isinstance(classifier, self.meta_model.SingletonType)
        self.item_by_xmi_id[object_info.xmi_id] = self.meta_model.SingletonValue(name, classifier)
        
        

        
    def _build_objects(self, root_element): 
        
        object_infos = self._get_object_infos(root_element)
        for info in object_infos:
            self._build_object(info)

            
            
            
       # type_infos = self._get_type_infos(root_element)
       # for info in type_infos:
       #     self._build_type(info)
        
        
    def fix_name(self, name, context):
        
        original_name = name
   
        name = name.replace('/', '_PER_')
        name = name.replace(',', '_COMMA_')
        name = name.replace('(', '_')
        name = name.replace(')', '_')
        
        if name != original_name:
            print(f"WARNING: {context} '{original_name}' renamed to '{name}'")
        check_is_symbol(name)
        
        return name

        
    def _build(self, element):
        
        
        
        xmi_id = element.get(XMI.id)
        
        
        if xmi_id == 'PrimitiveType0':
            ji=1
        
        built = self.item_by_xmi_id.get(xmi_id)
        if built:
            return built
         
        
        
        xmi_type = element.get(XMI.type)
       
        match xmi_type:
            case 'uml:Package':
                return self._build_package(element, self.meta_model.Package)
            case 'uml:Model':
                return self._build_package(element, self.meta_model.Model)
            

        
    def _build_package(self, package_element, package_class):
        name = package_element.attrib.get('name')
        
        if package_class is self.meta_model.Model:
            
            if 'process' in name.lower():
                
                package = package_class(name, 'http://dexpi.org/spec/process/1.0')
            else:
                package = package_class(name, 'http://dexpi.org/spec/plant/1.4')
        else:
            package = package_class(name)
            
        for child_element in package_element.findall('packagedElement'):
            built = self._build(child_element)
            if built is None:
                pass
            elif isinstance(built, self.meta_model.PackageableElement):
                if 1: # BUILTINS
                    package.packagedElements.add(built)
                    
                else:
                    if not isinstance(built, self.meta_model.PrimitiveType):
                        package.packagedElements.add(built)
            
        return package
    
    
    def _build_type_info(self, type_element, class_class):
        xmi_id = package_element.attrib.get(XMI.id)
        
        

        raise Exception(xmi_id)
        class_ = class_class(name)
        for child_element in package_element.findall('packagedElement'):
            built = self._build(child_element)
            if built is None:
                pass
            elif isinstance(built, self.meta_model.Package):
                package.packagedElements.add(built)
        return package


def read_xmi(source, meta_model=None, check_primitive_generalizations=False):
    
    reader = XmiReader(etree.parse(source).getroot(),meta_model=meta_model, check_primitive_generalizations=check_primitive_generalizations)
    return reader.package



from pnb.mcl.metamodel import standard as metamodel




@dataclass
class XmiConfiguration:
    uml_namespace: str = 'http://www.omg.org/spec/UML/20110701'
    xmi_namespace: str = 'http://schema.omg.org/spec/XMI/2.1'
    xmi_version: str = '2.1'
    root_element: str = '{http://www.omg.org/spec/UML/20110701}Model'
    primitive_type_prefix: T.Optional[str] = ''#'Primitive'
    generics: T.Literal['redefinition'] = 'redefinition'
    union_or: str = ' | '
    association_reference_in_property: bool = True # for EA


# TODO: remove 
  #      if 1 or mode == 'modelio':
  #          self.root = etree.Element('{http://www.omg.org/spec/UML/20110701}Model', nsmap={'uml': 'http://www.omg.org/spec/UML/20110701', 'xmi': 'http://schema.omg.org/spec/XMI/2.1'})
   #     else:
   #         self.root = etree.Element(XMI.XMI, nsmap={'uml': 'http://www.omg.org/spec/UML/20161101', 'xmi': 'http://schema.omg.org/spec/XMI/2.1'})
   #     self.root.attrib[XMI.version] = '2.1'



class XmiWriter:

    def __init__(self, model_set, configuration=XmiConfiguration()):

        self.configuration = configuration
        
        self.configuration

        self.id_by_element = {}
        self._auxiliary_type_elements = []
        self._super_type_refs_by_sub_type_ref = {}
        
        self._current_package_xmls = []

        self._xmi = XmlNamespace(configuration.xmi_namespace)
        nsmap = {
            'uml': configuration.uml_namespace,
            'xmi': configuration.xmi_namespace}
        self.root = etree.Element(configuration.root_element, nsmap=nsmap)
        self.root.attrib[self._xmi.version] = configuration.xmi_version

        for model in sorted(model_set, key=lambda model: model.name):
            self.root.extend(self._on_element(model, 'packagedElement'))

        if self._auxiliary_type_elements:
            auxiliary_package_xml = etree.Element('packagedElement', {
                XMI.type: 'uml:Model',
                'name': '_Auxiliaries'})
            auxiliary_package_xml.extend(self._auxiliary_type_elements)
            self.root.insert(0, auxiliary_package_xml)
            
            for element in self.root.iterdescendants():
                for super_type_id in self._super_type_refs_by_sub_type_ref.get(element.attrib.get(self._xmi.id), []):
                    etree.SubElement(element, 'generalization', {
                    XMI.type: f'uml:Generalization',
                    'general': super_type_id})
                    

            
    def get_id(self, element):
        id_ = self.id_by_element.get(element)
        if id_ is None:
            id_ = f'ID{len(self.id_by_element)}'
            self.id_by_element[element] = id_
        return id_
            
            
            
    def _on_element(self, element, tag):
        
        xml = None

        if isinstance(element, (metamodel.Package, metamodel.Model)):
            xml = etree.Element(tag, {
                XMI.type: f'uml:{element.get_meta_class_name()}',
                XMI.id: self.get_id(element),
                'name': element.name})
            self._current_package_xmls.append(xml)
            if isinstance(element, metamodel.Model):
                xml.attrib['URI'] = element.uri
            for member in element.packagedElements:
                xml.extend(self._on_element(member, 'packagedElement'))
            self._current_package_xmls.pop()

        elif isinstance(element, metamodel.Type):
            uml_type_name = {
                metamodel.AbstractClass: 'Class',
                metamodel.AbstractDataType: 'DataType',
                metamodel.AggregatedDataType: 'DataType',
                metamodel.BooleanType: 'PrimitiveType',
                metamodel.ConcreteClass: 'Class',
                metamodel.DateTimeType: 'PrimitiveType',
                metamodel.DoubleType: 'PrimitiveType',
                metamodel.Enumeration: 'Enumeration',
                metamodel.IntegerType: 'PrimitiveType',
                metamodel.StringType: 'PrimitiveType',
                metamodel.UndefinedType: 'PrimitiveType'}[type(element)]
            name = element.name
            if self.configuration.primitive_type_prefix and uml_type_name == 'PrimitiveType':
                name = self.configuration.primitive_type_prefix + name
            xml = etree.Element(tag, {
                XMI.type: f'uml:{uml_type_name}',
                XMI.id: self.get_id(element),
                'name': name})
            if element.isAbstract:
                xml.attrib['isAbstract'] = 'true'
            for super_type in element.superTypes:
                etree.SubElement(xml, 'generalization', {
                    XMI.type: f'uml:Generalization',
                    'general': self.get_id(super_type)})
            for attribute in element.ownedAttributes:
                xml.extend(self._on_element(attribute, 'ownedAttribute'))

            assert self.configuration.generics == 'redefinition'
            # TODO: otherwise, add owned parameters here

            if isinstance(element, metamodel.Enumeration):
                for literal in element.orderedOwnedLiterals:
                    xml.extend(self._on_element(literal, 'ownedLiteral'))
  
        elif isinstance(element, metamodel.EnumerationLiteral):
            xml = etree.Element(tag, {
                XMI.type: 'uml:EnumerationLiteral',
                XMI.id: self.get_id(element),
                'name': element.name})
            
        elif isinstance(element, metamodel.Property):
            prop_id = self.get_id(element)
            xml = etree.Element(tag, {
                XMI.type: 'uml:Property',
                XMI.id: prop_id,
                'name': element.name})
            if element.isOrdered:
                xml.attrib['isOrdered'] = 'true'
            if not element.isUnique:
                xml.attrib['isUnique'] = 'false'
            if element.lower != 1:
                xml.append(self._literal_integer(element.lower, 'lowerValue'))
            if element.upper != 1:
                xml.append(self._literal_unlimited_natural(element.upper, 'upperValue'))
            xml.attrib['type'] = self._get_type_reference(element.type)
            
            if isinstance(element, metamodel.ObjectProperty):
                if isinstance(element, metamodel.CompositionProperty):
                    xml.attrib['aggregation'] = 'composite'
                opp_prop_id = self.get_id(('opposite', element))
                assoc_id = self.get_id(('association', element))
                assoc_xml = etree.Element('packagedElement', {
                    XMI.type: 'uml:Association',
                    XMI.id: assoc_id,
                    'memberEnd': f'{prop_id} {opp_prop_id}'})
                self._current_package_xmls[-1].append(assoc_xml)
                opp_prop_xml = etree.Element('ownedEnd', {
                    XMI.type: 'uml:Property',
                    XMI.id: opp_prop_id})
                assoc_xml.append(opp_prop_xml)
                opp_prop_xml.attrib['isUnique'] = 'false'
                if element.oppositeLower != 1:
                    opp_prop_xml.append(self._literal_integer(element.oppositeLower, 'lowerValue'))
                if element.oppositeUpper != 1:
                    opp_prop_xml.append(self._literal_unlimited_natural(element.oppositeUpper, 'upperValue'))
                opp_prop_xml.attrib['type'] = self._get_type_reference(element.owner)
                if self.configuration.association_reference_in_property:
                    pass # TODO


        if xml is None:
            warnings.warn(type(element))
            return []
        return [xml]

    def _literal_integer(self, value: int, tag: str):
        xml = etree.Element(tag, {XMI.type: 'uml:LiteralInteger'})
        if value:
            xml.attrib['value'] = str(value)
        return xml

    def _literal_unlimited_natural(self, value: T.Optional[int], tag: str):
        xml = etree.Element(tag, {XMI.type: 'uml:LiteralUnlimitedNatural'})
        if value is None:
            xml.attrib['value'] = '*'
        elif value:
            xml.attrib['value'] = str(value)
        return xml
    
    def _get_type_reference(self, type_expression: metamodel.TypeExpression):
        assert isinstance(type_expression, metamodel.TypeExpression), type_expression
        
        if isinstance(type_expression, metamodel.Type):
            return self.get_id(type_expression)
        

        
        elif isinstance(type_expression, metamodel.UnionType):
            
            base_type_references = [self._get_type_reference(base) for base in type_expression.bases]
            if 'TODO' in base_type_references:
                return 'TODO'

            if isinstance(type_expression, metamodel.DataTypeExpression):
                uml_type_name = 'DataType'
            else:
                assert isinstance(type_expression, metamodel.ClassExpression)
                uml_type_name = 'Class'

            key = tuple([uml_type_name] + base_type_references)

            type_reference = self.id_by_element.get(key)
            if type_reference:
                return type_reference

            type_reference = self.get_id(key)
            name = self._get_type_expression_name(type_expression)
            if name.startswith('('):
                assert name.endswith(')')
                name = name[1:-1]
            
            type_element = etree.Element('packagedElement', {
                XMI.type: f'uml:{uml_type_name}',
                XMI.id: type_reference,
                'name': name,
                'isAbstract': 'true'})
            self._auxiliary_type_elements.append(type_element)
            
            for base_type_ref in base_type_references:
                self._super_type_refs_by_sub_type_ref.setdefault(base_type_ref, []).append(type_reference)

            return type_reference

        
        elif isinstance(type_expression, metamodel.TypeParameter):
            assert self.configuration.generics == 'redefinition'
            return self._get_type_reference(type_expression.type)
        
        else:
            assert self.configuration.generics == 'redefinition'
            assert isinstance(type_expression, metamodel.BoundType)
            
            base_type_reference = self._get_type_reference(type_expression.base)
            
            binding_references = [
                (self.get_id(binding.parameter), self._get_type_reference(binding.type))
                for binding in type_expression.bindings]
            
            if isinstance(type_expression, metamodel.DataTypeExpression):
                uml_type_name = 'DataType'
            else:
                assert isinstance(type_expression, metamodel.ClassExpression)
                uml_type_name = 'Class'
            
            
            key = tuple([uml_type_name, 'bound', base_type_reference] + binding_references)
            
            type_reference = self.id_by_element.get(key)
            if type_reference:
                return type_reference
            
            type_reference = self.get_id(key)
            name = self._get_type_expression_name(type_expression)

            if name.startswith('('):
                assert name.endswith(')')
                name = name[1:-1]
            
            type_element = etree.Element('packagedElement', {
                XMI.type: f'uml:{uml_type_name}',
                XMI.id: type_reference,
                'name': name,
                'isAbstract': 'true'})
            self._auxiliary_type_elements.append(type_element)
            
            self._super_type_refs_by_sub_type_ref.setdefault(type_reference, []).append(base_type_reference)

            for binding in type_expression.bindings:
                parameter = binding.parameter
                for prop in type_expression.base.ownedAttributes:
                    if prop.type is parameter:

                        prop_id = self.get_id((binding, prop))
                        xml = etree.Element('ownedAttribute', {
                            XMI.type: 'uml:Property',
                            XMI.id: prop_id,
                            'name': prop.name,
                            'redefinedProperty': self.get_id(prop)})
                        type_element.append(xml)
                        if prop.isOrdered:
                            xml.attrib['isOrdered'] = 'true'
                        if not prop.isUnique:
                            xml.attrib['isUnique'] = 'false'
                        if prop.lower != 1:
                            xml.append(self._literal_integer(prop.lower, 'lowerValue'))
                        if prop.upper != 1:
                            xml.append(self._literal_unlimited_natural(prop.upper, 'upperValue'))
                        xml.attrib['type'] = self._get_type_reference(binding.type)
                        
                        if isinstance(prop, metamodel.ObjectProperty):
                            ko
                            if isinstance(prop, metamodel.CompositionProperty):
                                xml.attrib['aggregation'] = 'composite'
                            opp_prop_id = self.get_id(('opposite', binding, prop))
                            assoc_id = self.get_id(('association', binding, prop))
                            assoc_xml = etree.Element('packagedElement', {
                                XMI.type: 'uml:Association',
                                XMI.id: assoc_id,
                                'memberEnd': f'{prop_id} {opp_prop_id}'})
                            self._auxiliary_type_elements.append(assoc_xml)
                            opp_prop_xml = etree.Element('ownedEnd', {
                                XMI.type: 'uml:Property',
                                XMI.id: opp_prop_id,
                              #  'redefinedProperty': self.get_id(('opposite', prop))})
                                })
                            assoc_xml.append(opp_prop_xml)
                            #TODO : check details of opp prop
                            opp_prop_xml.attrib['isUnique'] = 'false'
                            if prop.oppositeLower != 1:
                                opp_prop_xml.append(self._literal_integer(0, 'lowerValue'))
                            if prop.oppositeUpper != 1:
                                opp_prop_xml.append(self._literal_unlimited_natural(prop.oppositeUpper, 'upperValue'))
                            opp_prop_xml.attrib['type'] = type_reference
                            if self.configuration.association_reference_in_property:
                                pass # TODO
                        

            
            
            # TODO: redef

            return type_reference

    
    def _get_type_expression_name(self, type_expression: metamodel.TypeExpression):
        
        if isinstance(type_expression, metamodel.Type):
            return type_expression.name
        
        elif isinstance(type_expression, metamodel.UnionType):
            base_names = [self._get_type_expression_name(base) for base in type_expression.bases]
            if len(base_names) == 1:
                return base_names[0]
            else:
                return f'({self.configuration.union_or.join(base_names)})'
 
        elif isinstance(type_expression, metamodel.BoundType):
            name = type_expression.base.name
            if type_expression.bindings:
                bindings_repr = ', '.join(
                    f'{binding.parameter.name}={self._get_type_expression_name(binding.type)}'
                    for binding in type_expression.bindings)
                name = f'({name} with {bindings_repr})'
            return name

        
        
        
