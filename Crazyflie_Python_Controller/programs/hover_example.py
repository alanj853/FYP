import time

def _hover(time_in_seconds):
    target_alt = _getCurrentAltitude() + 4;
    current_time = time.time(); target_time = current_time + time_in_seconds;
        
    while current_time <= target_time:
        current_alt = _getCurrentAltitude();
        current_time = time.time();
        if current_alt < target_alt:
            _speedUp();
        elif current_alt > target_alt:
            _slowDown();
        else:
            print "Perfect thrust assinged. You are now hovering!!!";
        
        

def _speedUp():
    print "speeding up...";

def _slowDown():
    print "slowing down...";


def _getCurrentAltitude():
    return 4;

_hover(1);
print "done"
