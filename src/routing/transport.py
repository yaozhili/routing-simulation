import parse
import json
import threading
import socket

class Transport:

  TYPE = 'Transport'

  def __init__(self):
    pass

  def init(self, name, ip, port, hns_ip, hns_port):
    """Initialize
    Set the listen port and create a new thread to listen the port. 
    Args:
      name: name of local host,
      ip: ip to be listened,
      port: port to be listened
    """
    self._name, self._address = name, (ip, port)
    self._hns_address = (hns_ip, hns_port)
    self._mapping_table = {'hns': self._hns_address}
    self._mapping_lock = threading.Lock()
    self._debug = True
    self._running = False

  # to be finished
  def inject(self, routing_table, dispather, neighbor):
    """ Inject dependency
    """
    self.routing_table, self.dispather, self.neighbor = routing_table, dispather, neighbor

  def run(self):
    """ Run this module
    """
    # to be finished
    self.dispather.register(Transport.TYPE, transport_module)

    self._running = True
    #create a new thread and listen to specified address
    self._thread_listen = threading.Thread(target = self._listen, args = ())
    self._thread_listen.start()
    
    self._send_to_hns()

  def _send_to_hns(self):
    """ Send to hns to register itself
    """
    data = {
      'type': Transport.TYPE,
      'data': {
        self._name: self._address
      }
    }
    self.send('hns', data, False)

  def receive(self, data):
    """ Receive hns data
      Args:
        data: {
          'data': dict, a mapping table
        } 
    """
    mt = {}
    for key in data:
      mt[key] = (data[key][0], data[key][1])
    self._mapping_lock.acquire()
    self._mapping_table.update(mt)
    self._mapping_lock.release()

  def _listen(self):
    """ Start server
    Create a server socket and listen to specified address. 
    """
    print("Server listenning at %s:%d" % self._address)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(self._address)
    while True:
      if not self._running:
        break
      data, addr = s.recvfrom(10240)
      print('%s receive data\n' % self._name)
      data = parse.parse(data)
      self._process(data)
    s.close()

  def _process(self, data):
    """ Process data on transport layer
      Args:
        data: {
          'next_name': str
          'last_name': str
          'broadcasting': bool
          'visited': list
          'datagram': {
            'src': src
            'dest': dest
            'data': {
              'type':...
              'data':...
            }
          }
        }
    """
    # broadcasting
    if data['broadcasting']:
      self.broadcasting({
          'visited': data['visited'],
          'src': data['datagram']['src'],
          'data': data['datagram']['data']
        })
    
    # dispath to other module
    if data['datagram']['dest'] == self._name:
      # to be finished
      self.dispather.dispath(data['datagram']['data']['type'],
                          data['datagram']['data']['data'])
      if self._debug:
        print('receive data, need dispathing', data)
    # just route to other host
    else:
      if self._debug:
        print('routing from %s to %s'
                     % (data['datagram']['src'], data['datagram']['dest']))
      self.send(data['datagram']['dest'], data['datagram']['data'], False)

  def send(self, destination, data, privileged_mode = False):
    """ Send data to destination

    Send data, which can be normal data or router table, to destination.

    Args:
      destination: str, the name of destination host
      data: dict, {
        'type': ...
        'data': ...
      }
      privileged_mode: if set True, it can send it to destination directly, ignoring
                      the next hop router
    """
    # make a frame
    datagram = self._make_datagram(self._name, destination, data)
    frame = self._make_frame(destination, datagram, False, [], privileged_mode)

    if frame is None:
      if self._debug:
        print('fail to make a frame, canceling sending')
      return

    self._send_by_frame(frame)


  def _send_by_frame(self, frame):
    """ Send a frame to destination
      Args:
        frame: frame, including destination
    """
    # get sending address
    sending_address = self._get_address(frame['next_name'])

    if sending_address is None:
      if self._debug:
        print('%s not in mapping_table, canceling sending' % frame['next_name'])
      return

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(json.dumps(frame).encode(), sending_address)
    if self._debug:
      print('%s: succeed sending to %s' % (self._name, frame['next_name']))
    
    s.close()

  def broadcasting(self, data):
    """ Send to all neighbors
      Args: 
        data: {                        {
          'type': ...,        or          'visited': list,
                                          'src': str, source hostname   
          'data': ...                      'data': data same as left data
        }                                }
    """
    src = (self._name, data['src'])[data['src'] is None]
    visited = ([], data['visited'])[data['visited'] is None]
    data = (data, data['data'])[data['src'] is None]
    
    # to be finished
    neighbors = list(self.neighbor.get().keys())
    if self._debug:
      neighbors = ['B', 'C']
    for n in neighbors:
      if n not in visited:
        frame = self._make_frame(n, self._make_datagram(src, n, data),
                                    True, visited, False)
        if frame is None:
          if self._debug:
            print('fail to make a frame, canceling sending')
          continue

        self._send_by_frame(frame)


  def _make_datagram(self, src, dest, data):
    """ Make a datagram, which just like an ip datagram
      Args:
        src: str, source hostname
        dest: str, destination hostname
        data: data to be encapsulated

      Returns:
        datagram: json-like dict, {
          'src': src
          'dest': dest
          'data': data
        }
    """
    return {
      'src': src,
      'dest': dest,
      'data': data
    }

  def _make_frame(self, dest, datagram, broadcasting, visited, privileged_mode):
    """ Make a frame, which just like link-layer frame
      Args:
        dest: str, destination hostname, used to get next hop router
        data: an datagram
        broadcasting: bool, whether broadcasting
        visited: list, list of visited hostname
        privileged_mode: bool, if set True, it can send it to destination directly,
                      ignoring the next hop router

      Returns:
        frame: if succeed making a frame, then return it, otherwise, return None
          {
            'next_name': str, next hop hostname name
            'last_name': str, always be self name
            'broadcasting': bool
            'visited': list
            'datagram': datagram
          }
    """
    # to be finished
    try:
      next_name = (dest, self.routing_table.get(dest))[privileged_mode or broadcasting]
      # if self._debug:
      #   next_name = (dest, dest)[privileged_mode or broadcasting]
    except:
      return None

    if broadcasting:
      visited.append(self._name)

    return {
      'next_name': next_name,
      'last_name': self._name,
      'broadcasting': broadcasting,
      'visited': visited,
      'datagram': datagram
    }

  def _get_address(self, dest):
    """ Get ip address by name
      Args:
        dest: str, destination hostname
      Returns:
        address: (ip, port) or None
    """
    self._mapping_lock.acquire()
    try:
      address = self._mapping_table[dest]
    except:
      address = None
    self._mapping_lock.release()

    return address