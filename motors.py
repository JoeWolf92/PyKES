import time
import serial
import io

class smc100:

    busy_list = []

    def open_port(self, portname):
        
        port_1 = serial.Serial(port=portname,
                baudrate=57600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=0.1)    
        
        sio = io.TextIOWrapper(io.BufferedRWPair(port_1, port_1))
        
        return sio


    def move_to_pos(self, ctr_adr, pos, port): 
                
        while port in self.busy_list:
            time.sleep(0.01)
        self.busy_list.append(port)

        port.write(ctr_adr+"PA"+pos+"\r\n".encode('utf-8'))
        port.flush()
                
        self.busy_list.remove(port)
        
    def find_home(self, ctr_adr, port):
    
        while port in self.busy_list:
            time.sleep(0.01)
        self.busy_list.append(port)

        port.write(unicode(str(ctr_adr)+"OR\r\n"))
        port.flush()

        self.busy_list.remove(port)


    def stop(self,ctr_adr, port):
                    
        while port in self.busy_list:
            time.sleep(0.01)
        self.busy_list.append(port)

        port.write(unicode(str(ctr_adr)+"ST\r\n"))
        port.flush()

        self.busy_list.remove(port)

        
                
    def current_position(self, ctr_adr, port):
        
        while port in self.busy_list:
	        time.sleep(0.05)
                
        self.busy_list.append(port)
        
        cur_pos = ""                        
    
        while cur_pos=="":
		
	    try:
	        time.sleep(0.05)
                port.write(unicode(str(ctr_adr)+"TP\r\n"))
                port.flush()
                time.sleep(0.05)
		cur_pos = port.readline()
		
            except:
		cur_pos=""

            try:
        	cur_pos = float(cur_pos.split("TP")[1])
            except:
        	cur_pos=""

        self.busy_list.remove(port)
            
	return cur_pos

    def status(self, ctr_adr, port):
        
        while port in self.busy_list:
            time.sleep(0.05)
            
        self.busy_list.append(port)
		
        sts = ""
		
        while sts =="":
            
            try:
                time.sleep(0.05)
                port.write(unicode(str(ctr_adr)+"TS\r\n"))
                port.flush()
                time.sleep(0.05)
                sts = port.readline()
            except:
                sts=""
	
	sts = sts[7:9]
	
        if sts == "28":

            status = "MOVING"

        elif any([sts == str(a) for a in range(32,36)]):
                
	    status = "READY"
            
	else:
	    status = "ERROR"

        self.busy_list.remove(port)
         
        return status

    def enable(self, ctr_adr, port):
        
	port.write(unicode(str(ctr_adr)+"MM1\r\n"))
        port.flush()
        
        return

    def disable(self, ctr_adr, port):

        port.write(unicode(str(ctr_adr)+"MM0\r\n"))
        port.flush()
        
        return
