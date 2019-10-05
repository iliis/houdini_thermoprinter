extern crate thermal_printer;

use thermal_printer::prelude::*;


// we're accessing the printer over USB, which appears as a file instead of a serial port, but our
// library wants the serial::Write trait

struct File(pub std::fs::File);

impl thermal_printer::prelude::_thermal_printer_serial_Write<u8> for File
{
    type Error = std::io::Error;

    fn write(&mut self, word: u8) -> Result<(), Self::Error> {
        self.write(word);
    }

    fn flush(&mut self) -> Result<(), Self::Error> {
        Ok()
    }
}


fn main() {
    let mut printer_handle = match File::open("/dev/usb/lp0") {
        Ok(file) => file,
        Err(err) => panic!("Unable to talk to printer: {}", err),
    };

    let mut printer = ThermalPrinter::new(printer_handle);

    println!("Hello, world!");
}
