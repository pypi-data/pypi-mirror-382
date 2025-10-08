# pupyC3D (c) by Antoine MARIN antoine.marin@univ-rennes2.fr
#
# pupyC3D is licensed under a
# Creative Commons Attribution-NonCommercial 4.0 International License.
#
# You should have received a copy of the license along with this
# work. If not, see <https://creativecommons.org/licenses/by-nc/4.0/>.

import os
import warnings
import struct
import math
import numpy as np
from .decoder import *

class Metadata:
    """Base class for Parameters and ParameterGroups.
    
    Handles common functionality for C3D metadata elements including
    name, description, and group ID management.
    """

    def __init__(self, name:str, group_id:int):
        """Initialize metadata object.
        
        Args:
            name (str): Name of the metadata element
            group_id (int): ID of the parameter group
        """
        self.name = name
        self.description = ''
        self.group_id = group_id

    def read_from_buffer(self, buffer:ProcStream):
        """Read metadata from binary buffer.
        
        Args:
            buffer (ProcStream): Binary data stream
            
        Returns:
            int: Number of bytes read
        """
        return 0

    def write_to_buffer(self, buffer: ProcStream):
        """Write metadata to binary buffer.
        
        Args:
            buffer (ProcStream): Binary data stream to write to
        """
        buffer.write_int8(len(self.name))
        buffer.write_int8(self.group_id)
        buffer.write_string(self.name)

    def _get_offset(self):
        """Calculate byte offset for metadata structure.
        
        Returns:
            int: Offset in bytes
        """
        return 2 + len(self.description) + 1

    def get_size(self):
        """Calculate total size of metadata structure.
        
        Returns:
            int: Total size in bytes
        """
        return 2 + len(self.name) + self._get_offset()


class Parameter(Metadata):
    """Represents a C3D parameter with typed data.
    
    Parameters can store scalar values or multi-dimensional arrays
    of various types (int8, uint16, float, string).
    """

    def __init__(self, name:str, group_id:int):
        """Initialize parameter.
        
        Args:
            name (str): Parameter name
            group_id (int): ID of the parameter group
        """
        super(Parameter, self).__init__(name, group_id)
        self.data_type = 0
        self.value = None

    def read_from_buffer(self, buffer:ProcStream):
        """Read parameter data from binary buffer.
        
        Supports scalar and multi-dimensional array data of types:
        - int8 (data_type=1)
        - uint16 (data_type=2) 
        - float (data_type=4)
        - string (data_type=-1)
        
        Args:
            buffer (ProcStream): Binary data stream
            
        Returns:
            int: Number of bytes read
        """
        offset = 0
        self.data_type = buffer.get_int8()
        offset += 1
        n_dim = buffer.get_int8()
        offset += 1
        if n_dim == 0:
            if self.data_type == 1:
                self.value = buffer.get_int8()
            elif self.data_type == 2:
                self.value = buffer.get_uint16()
            elif self.data_type == 4:
                self.value = buffer.get_float()
            data_size = abs(self.data_type)
        else:
            dims = []
            for i in range(n_dim):
                dims.append(buffer.get_uint8())
                offset += 1
            prod = math.prod(dims[:n_dim])
            if self.data_type == -1:
                if len(dims) >= 2:
                    row = 1
                    inc2 = 1
                    while inc2 < n_dim:
                        row *= dims[inc2]
                        inc2 += 1
                    data = []
                    for i in range(row):
                        data.append(buffer.get_string(dims[0]).strip())
                    data = np.array(data)
                    if data.size == 0:
                        data = np.empty((dims[:]), str)
                else:
                    data = np.array([buffer.get_string(prod).strip()])
            elif self.data_type == 1:
                data = np.array([buffer.get_int8() for _ in range(prod)]).reshape(dims[::-1])
            elif self.data_type == 2:
                data = np.array([buffer.get_uint16() for _ in range(prod)]).reshape(dims[::-1])
            elif self.data_type == 4:
                data = np.array([buffer.get_float() for _ in range(prod)]).reshape(dims[::-1])
            else:
                data = np.array([])

            self.value = data
            data_size = prod * abs(self.data_type)
        offset += data_size
        desc_len = buffer.get_uint8()
        self.description = buffer.get_string(desc_len)
        offset += desc_len
        return offset

    def write_to_buffer(self, buffer: ProcStream, last_entry=False):
        super(Parameter, self).write_to_buffer(buffer)
        if last_entry:
            offset = 0
        else:
            offset = self._get_offset()
        buffer.write_uint16(offset)
        buffer.write_int8(self.data_type)

        dims = self.__get_dim()
        n_dim = len(dims)
        buffer.write_int8(n_dim)
        if n_dim == 0:
            if self.data_type == 1:
                buffer.write_int8(self.value)
            elif self.data_type == 2:
                buffer.write_uint16(self.value)
            elif self.data_type == 4:
                buffer.write_float(self.value)
        else:
            for each in dims:
                buffer.write_uint8(each)
            data = self.value.flatten()
            for each in data:
                if self.data_type == 1:
                    buffer.write_int8(each)
                elif self.data_type == 2:
                    buffer.write_uint16(each)
                elif self.data_type == 4:
                    buffer.write_float(each)
                elif self.data_type == -1:
                    buffer.write_string(each.ljust(dims[0]))

        buffer.write_uint8(len(self.description))
        buffer.write_string(self.description)

    def _get_offset(self):
        offset = 2 + 1 + 1 #offset, data_type, dim
        if not isinstance(self.value, np.ndarray):
            offset += self.data_type#value
        else:
            # n_dimension
            dims = self.__get_dim()
            n_dim = len(dims)
            offset += n_dim
            # data size
            prod = math.prod(dims[:n_dim])
            data_size = prod * abs(self.data_type)
            offset += data_size

        offset +=1 # desc length
        offset += len(self.description) #desc
        return offset

    def __get_dim(self):
        if not isinstance(self.value, np.ndarray):
            dims  = []
        else:
            dims = self.value.shape
            if self.data_type == -1:
                if dims[0] == 1:
                    dims = [len(self.value[0])]
                else:
                    if self.value.size > 0:
                        d1 = max([len(x) for x in self.value])
                        dims = [d1, dims[0]]
        return dims


class ParameterGroup(Metadata):
    """Represents a group of related C3D parameters.
    
    Parameter groups organize parameters by functionality
    (e.g., POINT, ANALOG, TRIAL groups).
    """

    def __init__(self, name:str, group_id:int):
        """Initialize parameter group.
        
        Args:
            name (str): Group name
            group_id (int): Unique group identifier
        """
        super(ParameterGroup, self).__init__(name, group_id)
        self.parameters = dict()

    def add_parameter(self, name)->Parameter:
        """Add a new parameter to this group.
        
        Args:
            name (str): Parameter name
            
        Returns:
            Parameter: New or existing parameter
        """
        if name not in self.parameters:
            param = Parameter(name, -self.group_id)
            self.parameters[param.name] = param
            return param
        warnings.warn('Parameter %s already exists' %name)
        return self.parameters[name]

    def remove_parameter(self, name):
        """Remove a parameter from this group.
        
        Args:
            name (str): Parameter name to remove
            
        Returns:
            bool: True if parameter was removed, False if not found
        """
        if name in self.parameters:
            self.parameters.pop(name)
            return True
        return False

    def get_parameter(self, name):
        """Get a parameter by name.
        
        Args:
            name (str): Parameter name
            
        Returns:
            Parameter or None: Parameter object if found
        """
        if name not in self.parameters:
            return None
        return self.parameters[name]

    def read_from_buffer(self, buffer:ProcStream):
        desc_len = buffer.get_uint8()
        offset = 1
        desc = buffer.get_string(desc_len)
        offset += desc_len
        self.description = desc
        return offset

    def write_to_buffer(self, buffer: ProcStream, last_entry=False):
        super(ParameterGroup, self).write_to_buffer(buffer)
        # offset = 2 + len(self.description) + 1
        offset = self._get_offset()
        buffer.write_uint16(offset)
        buffer.write_uint8(len(self.description))
        buffer.write_string(self.description)


class C3DFile:
    """Main class for reading and writing C3D files.
    
    C3D files contain 3D coordinate data, parameters, and metadata
    commonly used in biomechanics and motion capture applications.
    
    Attributes:
        filename (str): Path to the C3D file
        header (dict): File header information
        groups (dict): Parameter groups indexed by group ID
        data (dict): Point and analog data
    """

    def __init__(self, filename:str=''):
        """Initialize C3DFile object.
        
        Args:
            filename (str, optional): Path to C3D file. If file exists,
                it will be automatically loaded.
        """
        self.filename = filename
        self.__decoder = None
        self.header = dict()
        self.groups = dict()
        self.data = dict()
        if os.path.exists(filename):
            self.read_file()

    def read_file(self):
        """
        Read the C3D file associated with self.filename
        """
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as handle:
                self.__read_header(handle)
                self.__read_parameters(handle)
                self.__read_data(handle)
        else:
            raise FileNotFoundError(self.filename)

    def write(self, filename:str='', **kwargs):
        """Write C3D data to file.
        
        Args:
            filename (str, optional): Output file path. Defaults to self.filename.
            **kwargs: Additional options:
                overwrite (bool): Allow overwriting existing file. Defaults to False.
                
        Raises:
            Warning: If file exists and overwrite=False
        """
        overwrite = kwargs.get('overwrite', False)
        if filename == '':
            filename = self.filename
        if os.path.exists(filename) and not overwrite:
            warnings.warn('File %s already exist. If you wish to overwrite it set ''overwrite'' argument to True' %filename)
            return
        with open(filename, 'wb') as handle:
            self.__write_header(handle)
            self.__write_parameters(handle)
            self.__write_data(handle)

    def add_parameter_group(self, name, gid=0)->ParameterGroup:
        """Add a new parameter group.
        
        Args:
            name (str): Group name
            gid (int, optional): Group ID. If 0, auto-assigned. Defaults to 0.
            
        Returns:
            ParameterGroup or None: New group if created, None if already exists
        """
        assert(gid <= 0)
        if gid == 0:
            g = self.get_parameter_group(name)
        else:
            g = self.get_parameter_group(gid)
        if g is not None:
            return None
        if gid == 0:
            ids = list(self.groups.keys())
            gid = ids[0]
            # find first missing id
            for number in ids:
                if number != gid:
                    break
                gid -= 1
        self.groups[gid] = ParameterGroup(name, gid)
        return self.groups[gid]

    def remove_parameter_group(self, group)->bool:
        """Remove a parameter group.
        
        Args:
            group (int or str): Group ID or name
            
        Returns:
            bool: True if group was removed, False if not found
        """
        g = self.get_parameter_group(group)
        if g is not None:
            self.groups.pop(g.group_id)
            return True
        return False

    def get_parameter_group(self, group_id)->ParameterGroup:
        """Get a parameter group by ID or name.
        
        Args:
            group_id (int or str): Group ID or name
            
        Returns:
            ParameterGroup or None: Parameter group if found
            
        Raises:
            TypeError: If group_id is neither int nor str
        """
        if isinstance(group_id, int):
            return self.groups.get(group_id, None)
        elif isinstance(group_id, str):
            g = {v.name: v for v in self.groups.values()}
            return g.get(group_id, None)
        else:
            raise TypeError('Argument ''group_id'' should be either str or int')

    def add_parameter(self, name, gid):
        group = self.get_parameter_group(gid)
        if group is not None:
            param = group.add_parameter(name)
            return param
        return None

    def remove_parameter(self, name, group_id):
        g = self.get_parameter_group(group_id)
        if g is not None:
            return g.remove_parameter(name)
        return False

    def get_parameter(self, group_id, param_name):
        g = self.get_parameter_group(group_id)
        if g is not None:
            return g.parameters.get(param_name, None)
        return None

    def get_point_data(self, name: str):
        """
        Return trajectory of a point
        :param name: the point name in string
        :return: trajectory as np.ndarray (NbFrames X 3)
        """
        if name not in self.data['POINTS']:
            raise ValueError('Point %s does not exists!' %name)
        return self.data['POINTS'][name]

    def get_points_data(self, name_list:list[str]):
        """
        Get several points trajectories
        :param name_list: list of the points names
        :return: dict of name:trajectories data
        """
        return {name: self.get_point_data(name) for name in name_list}

    def get_point_names(self):
        """
        Get a list of all points in the c3d
        :return: List[str] with all points labels
        """
        return list(self.data['POINTS'].keys())

    def get_analog_data(self, name: str):
        """
        Return values for an analog chanel
        :param name: analog name in string
        :return: analog chanel values as np.ndarray(NbAnalogFrames X 1)
        """
        if name not in self.data['ANALOGS']:
            raise ValueError('Chanel %s does not exists!' %name)
        return self.data['ANALOGS'][name]

    def get_analogs_data(self, name_list:list[str]):
        """
        Get several analog channels
        :param name_list: list of the analogs names
        :return: dict of name:values data
        """
        return {name: self.get_analog_data(name) for name in name_list}

    def get_analog_names(self):
        """
        Get a list of all analogs chanels in the c3d
        :return: List[str] with all analogs labels
        """
        return list(self.data['ANALOGS'].keys())

    def get_rotation_data(self, name:str):
        """
        Return rotation data (mainly for c3d created by theia markerless software)
        :param name: Joint name
        :return: rotation and position data np.ndarray(NbFrames X 4 X 4)
        """
        if name not in self.data['ROTATIONS']:
            raise ValueError('Rotation %s does not exists!' %name)
        return self.data['ROTATIONS'][name]

    def get_rotations_data(self, name_list:list[str]):
        """
        Get several rotations data
        :param name_list: list of the rotations
        :return: dict of name:values data
        """
        return {name: self.get_rotation_data(name) for name in name_list}

    def get_rotation_names(self):
        """
        Get a list of all rotation data in the c3d
        :return: List[str] with all rotations labels
        """
        return list(self.data['ROTATIONS'].keys())

    @property
    def point_count(self):
        """
        Get the number of 3D points in the c3d
        :return: int
        """
        p = self.get_parameter('POINT', 'USED')
        return p.value

    @property
    def analog_count(self):
        """
        Get the number of analog channels in the c3d
        :return: int
        """
        p = self.get_parameter('ANALOG', 'USED')
        if p is not None:
            return p.value
        return 0

    @property
    def frame_count(self):
        """
        Get the number of 3D points frames
        :return: int
        """
        return self.header['last_frame'] - self.header['first_frame'] + 1

    @property
    def analog_frame_count(self):
        """
        Get the number of analog frames
        :return: int
        """
        if self.analog_count > 0:
            return self.frame_count * self.header['analog_per_frame']
        return 0

    @property
    def frame_rate(self):
        """
        Get the 3D points frame rate
        :return: float
        """
        p = self.get_parameter('POINT', 'RATE')
        return p.value

    @property
    def analog_rate(self):
        """
        Get the analog channels frame rate
        :return: float
        """
        p = self.get_parameter('ANALOG', 'RATE')
        if p is not None:
            return p.value
        return 0

    @property
    def point_unit(self):
        """
        Get the 3D points unit (usually mm or m)
        :return: str
        """
        p = self.get_parameter('POINT', 'UNITS')
        return p.value

    @property
    def analog_unit(self):
        """
        Get the analog channels unit (mV, V, ...)
        :return: str
        """
        p = self.get_parameter('ANALOG', 'UNITS')
        if p is not None:
            return p.value
        return []

    def __read_header(self, handle):
        handle.seek(0)
        # check if it's a c3d file
        self.header['parameter_block'], magic = struct.unpack('BB', handle.read(2))
        if magic != 80:
            warnings.warn('%s is not a c3d file!' %self.filename)
            return
        # go to the start of the parameter block
        handle.seek((self.header['parameter_block'] - 1) * 512 + 3)
        # find the good encoder
        processor = struct.unpack('B', handle.read(1))[0]
        if processor == PROCESSOR_INTEL:
            self.__decoder = DecoderIntel(handle)
        elif processor == PROCESSOR_DEC:
            self.__decoder = DecoderDec(handle)
        elif processor == PROCESSOR_MIPS:
            self.__decoder = DecoderMips(handle)

        #  start reading header
        handle.seek(2)
        self.header['point_count'] = self.__decoder.get_uint16()
        self.header['analog_count'] = self.__decoder.get_uint16()
        self.header['first_frame'] = self.__decoder.get_uint16()
        self.header['last_frame'] = self.__decoder.get_uint16()
        self.header['max_gap'] = self.__decoder.get_uint16()
        self.header['scale_factor'] = self.__decoder.get_float()
        self.header['data_block'] = self.__decoder.get_uint16()
        self.header['analog_per_frame'] = self.__decoder.get_uint16()
        if self.header['analog_per_frame'] > 0 and self.header['analog_count'] > 0:
            self.header['analog_count'] /= self.header['analog_per_frame']
            self.header['analog_count'] = int(self.header['analog_count'])
        if self.header['analog_per_frame'] == 0:
            self.header['analog_per_frame'] = 1
        self.header['frame_rate'] = self.__decoder.get_float()

        self.header['events'] = dict()
        handle.read(270)
        self.header['events']['label_range_section'] = self.__decoder.get_uint16()
        self.header['events']['label_first_block'] = self.__decoder.get_uint16()
        self.header['events']['label_event_fmt'] = self.__decoder.get_uint16()
        if self.header['events']['label_event_fmt'] == 12345:
            self.header['events']['long_event_labels'] = True
        else:
            self.header['events']['long_event_labels'] = False
        self.header['events']['num_events'] = self.__decoder.get_uint16()
        if self.header['events']['num_events'] > 0:
            self.header['events']['data'] = {'labels': [], 'time': [], 'display': []}
            handle.read(2)
            for i in range(self.header['events']['num_events']):
                self.header['events']['data']['time'].append(self.__decoder.get_float())
            handle.seek(198)
            print(handle.tell())
            for i in range(self.header['events']['num_events']):
                self.header['events']['data']['display'].append(self.__decoder.get_uint8())
                # print(self.header['events']['data']['display'][i])
            handle.seek(198 * 2)
            if self.header['events']['long_event_labels']:
                num_char = 4
            else:
                num_char = 2
            for i in range(self.header['events']['num_events']):
                name = self.__decoder.get_string(num_char)
                self.header['events']['data']['labels'].append(name)

    def __write_header(self, handle):
        if self.__decoder == 0:
            self.__decoder = DecoderIntel(handle)
        else:
            self.__decoder.handle = handle

        handle.seek(0)
        self.__decoder.write_uint8(self.header['parameter_block'])
        self.__decoder.write_uint8(80)

        if isinstance(self.__decoder, DecoderIntel):
            processor = PROCESSOR_INTEL
        elif isinstance(self.__decoder, DecoderDec):
            processor = PROCESSOR_DEC
        elif isinstance(self.__decoder, DecoderMips):
            processor = PROCESSOR_MIPS
        else:
            raise ValueError('Processor not supported')

        handle.seek((self.header['parameter_block'] - 1) * 512 + 3)
        self.__decoder.write_uint8(processor)

        handle.seek(2)
        p = self.get_parameter('POINT', 'USED')
        self.__decoder.write_uint16(p.value)
        if self.header['analog_per_frame'] > 0 and self.header['analog_count'] > 0:
            analog_count = self.header['analog_count']* self.header['analog_per_frame']
        else:
            analog_count = self.header['analog_count']
        self.__decoder.write_uint16(analog_count)
        self.__decoder.write_uint16(self.header['first_frame'])
        self.__decoder.write_uint16(self.header['last_frame'])
        self.__decoder.write_uint16(self.header['max_gap'])
        self.__decoder.write_float(self.header['scale_factor'])
        data_block = self.__get_parameters_blocknum() + 2
        self.__decoder.write_uint16(data_block)
        if self.header['analog_per_frame'] == 1:
            analog_per_frame = 0
        else:
            analog_per_frame = self.header['analog_per_frame']
        self.__decoder.write_uint16(analog_per_frame)
        self.__decoder.write_float(self.header['frame_rate'])

        handle.seek(handle.tell() + 270)
        self.__decoder.write_uint16(self.header['events']['label_range_section'])
        self.__decoder.write_uint16(self.header['events']['label_first_block'])
        self.__decoder.write_uint16(self.header['events']['label_event_fmt'])
        self.__decoder.write_uint16(self.header['events']['num_events'])
        if self.header['events']['num_events'] > 0:
            handle.seek(handle.tell() + 2)
            for i in range(self.header['events']['num_events']):
                self.__decoder.write_float(self.header['events']['data']['time'][i])
            handle.seek(198)
            print(handle.tell())
            for i in range(self.header['events']['num_events']):
                self.__decoder.write_uint8(self.header['events']['data']['display'][i])
            handle.seek(198 * 2)
            if self.header['events']['long_event_labels']:
                num_char = 4
            else:
                num_char = 2
            for i in range(self.header['events']['num_events']):
                name = self.header['events']['data']['labels'][i].ljust(num_char)
                self.__decoder.write_string(name)

    def __read_parameters(self, handle):
        handle.seek((self.header['parameter_block'] - 1) * 512)
        handle.read(4)
        last_entry = False
        while not last_entry:
            nb_char_label = self.__decoder.get_int8()
            if nb_char_label == 0:
                break
            group_id = self.__decoder.get_int8()
            name = self.__decoder.get_string(abs(nb_char_label))
            if group_id < 0:#group
                current = self.add_parameter_group(name, group_id)
            else:#parameter
                group = self.get_parameter_group(-group_id)
                if group is not None:
                    current = group.add_parameter(name)
                else :
                    current = Parameter(name, group_id)

            offset = self.__decoder.get_uint16()
            if offset == 0:
                last_entry = True
            offset -= 2
            offset -= current.read_from_buffer(self.__decoder)

    def __write_parameters(self, handle):
        handle.seek((self.header['parameter_block'] - 1) * 512 + 2)
        self.__decoder.write_uint8(self.__get_parameters_blocknum())
        handle.seek((self.header['parameter_block'] - 1) * 512+4)
        groups = list(self.groups.values())
        for g in groups:
            g.write_to_buffer(self.__decoder)
        for group in groups:
            params = list(group.parameters.values())
            for param in params:
                if group == groups[-1] and param == params[-1]:
                    param.write_to_buffer(self.__decoder, True)
                else:
                    param.write_to_buffer(self.__decoder)

    def __get_parameters_blocknum(self):
        parameters_size = 0
        for g in self.groups.values():
            parameters_size += g.get_size()
            for p in g.parameters.values():
                parameters_size += p.get_size()
        return math.ceil(parameters_size/512)

    def __read_data(self, handle):
        handle.seek((512 * (self.header['data_block'] - 1)))
        nb_frames = self.header['last_frame'] - self.header['first_frame'] + 1
        point_used = self.header['point_count']
        scale = abs(self.header['scale_factor'])
        is_float = self.header['scale_factor'] < 0
        if point_used > 0:
            point_scale = [scale, 1][is_float]
            names_param = self.get_parameter('POINT', 'LABELS')
            marker_names = names_param.value.tolist()
            self.data['POINTS'] = dict()
            for each in marker_names:
                self.data['POINTS'][each] = np.zeros([nb_frames, 4])

        analog_used = self.header['analog_count']
        if analog_used > 0:
            offsets = np.zeros((analog_used,), int)
            param = self.get_parameter('ANALOG', 'OFFSET')
            if param is not None:
                offsets = param.value

            scales = np.ones((analog_used,), float)
            param = self.get_parameter('ANALOG', 'SCALE')
            if param is not None:
                scales = param.value

            gen_scale = 1.
            param = self.get_parameter('ANALOG', 'GEN_SCALE')
            if param is not None:
                gen_scale = param.value
            names_param = self.get_parameter('ANALOG', 'LABELS')
            if names_param is not None:
                analog_names = names_param.value.tolist()

            self.data['ANALOGS'] = dict()
            for each in analog_names:
                self.data['ANALOGS'][each] = np.zeros([nb_frames*self.header['analog_per_frame'], 1])

        rot_param = self.get_parameter_group('ROTATION')
        if rot_param is not None:
            names_param = self.get_parameter('ROTATION', 'LABELS')
            rotation_names = names_param.value.tolist()
            self.data['ROTATIONS'] = dict()
            for each in rotation_names:
                self.data['ROTATIONS'][each] = np.zeros([nb_frames, 4, 4])

        for i in range(nb_frames):
            if point_used > 0:
                self.__read_point_frame(i, is_float, point_scale, marker_names)
            if analog_used >0:
                self.__read_analog_frame(i, is_float, self.header['analog_per_frame'], offsets, scales, gen_scale, analog_names)

        if rot_param is not None:
            data_start = self.get_parameter('ROTATION', 'DATA_START').value
            handle.seek((512 * (data_start - 1)))
            for i in range(nb_frames):
                self.__read_rotation_frame(i, rotation_names)

    def __read_point_frame(self, frame_num, is_float, point_scale, marker_names):
        for j, m in enumerate(marker_names):
            if is_float:
                p = np.array([self.__decoder.get_float(), self.__decoder.get_float(), self.__decoder.get_float(),
                              self.__decoder.get_float()])
            else:
                p = np.array([self.__decoder.get_uint16(), self.__decoder.get_uint16(), self.__decoder.get_uint16(),
                              self.__decoder.get_uint16()])
            p = p * point_scale
            self.data['POINTS'][m][frame_num, :] = p

    def __read_analog_frame(self, frame_num, is_float, sub_frames, offsets, scales, gen_scale, analog_names):
        if frame_num == 315:
            stop = 1
        for j in range(int(sub_frames)):
            for k, analog in enumerate(analog_names):
                if is_float:
                    c = self.__decoder.get_float()
                else:
                    c = self.__decoder.get_uint16()
                self.data['ANALOGS'][analog][frame_num*sub_frames+j] = (c-offsets[k]) * scales[k]*gen_scale

    def __read_rotation_frame(self, frame_num, rotation_names):
        for i, name in enumerate(rotation_names):
            p = np.array([[self.__decoder.get_float(), self.__decoder.get_float(), self.__decoder.get_float(),
                           self.__decoder.get_float()],
                          [self.__decoder.get_float(), self.__decoder.get_float(), self.__decoder.get_float(),
                           self.__decoder.get_float()],
                          [self.__decoder.get_float(), self.__decoder.get_float(), self.__decoder.get_float(),
                           self.__decoder.get_float()],
                          [self.__decoder.get_float(), self.__decoder.get_float(), self.__decoder.get_float(),
                           self.__decoder.get_float()]])
            self.data['ROTATIONS'][name][frame_num, :, :] = p.transpose()
            self.__decoder.get_float()

    def __write_data(self, handle):
        handle.seek((512 * (self.header['data_block'] - 1)))
        point_used = self.header['point_count']>0
        if point_used:
            scale = abs(self.header['scale_factor'])
            is_float = self.header['scale_factor'] < 0
            point_scale = [scale, 1][is_float]
            names_param = self.get_parameter('POINT', 'LABELS')
            marker_names = names_param.value.tolist()

        analog_used = self.header['analog_count']
        if analog_used > 0:
            offsets = np.zeros((analog_used,), int)
            param = self.get_parameter('ANALOG', 'OFFSET')
            if param is not None:
                offsets = param.value

            scales = np.ones((analog_used,), float)
            param = self.get_parameter('ANALOG', 'SCALE')
            if param is not None:
                scales = param.value

            gen_scale = 1.
            param = self.get_parameter('ANALOG', 'GEN_SCALE')
            if param is not None:
                gen_scale = param.value
            names_param = self.get_parameter('ANALOG', 'LABELS')
            if names_param is not None:
                analog_names = names_param.value.tolist()

        rot_param = self.get_parameter_group('ROTATION')
        if rot_param is not None:
            names_param = self.get_parameter('ROTATION', 'LABELS')
            rotation_names = names_param.value.tolist()

        nb_frames = self.header['last_frame'] - self.header['first_frame'] + 1
        for i in range(nb_frames):
            if point_used:
                self.__write_point_frame(marker_names, i, is_float, point_scale)
            if rot_param is not None:
                self.__write_rotation_frame(i, rotation_names)
            if analog_used:
                self.__write_analog_frame(i, self.header['analog_per_frame'], analog_names, is_float, scales, gen_scale, offsets)

    def __write_point_frame(self, marker_names, frame_num, is_float, point_scale):
        for j, m in enumerate(marker_names):
            p = self.data['POINTS'][m][frame_num, :]/point_scale
            for i in range(4):
                if is_float:
                    self.__decoder.write_float(p[i])
                else:
                    self.__decoder.write_uint16(p[i])

    def __write_analog_frame(self, frame_num, sub_frames, analog_names, is_float, scales, gen_scale, offsets):
        for j in range(int(sub_frames)):
            for k, analog in enumerate(analog_names):
                data = self.data['ANALOGS'][analog][frame_num*sub_frames+j]
                c = ((data/gen_scale/scales[k]))+offsets[k]
                if is_float:
                    self.__decoder.write_float(c)
                else:
                    self.__decoder.write_uint16(c)

    def __write_rotation_frame(self, frame_num, rotation_names):
        for i, name in enumerate(rotation_names):
            r = self.data['ROTATIONS'][name][frame_num, :, :].transpose()
            for j in range(4):
                for k in range(4):
                    self.__decoder.write_float(r[j,k])
