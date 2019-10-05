extern crate thermal_printer;
extern crate nb;

use std::io::Write;

use thermal_printer::prelude::*;


// we're accessing the printer over USB, which appears as a file instead of a serial port, but our
// library wants the serial::Write trait

struct File(pub std::fs::File);

impl thermal_printer::prelude::_thermal_printer_serial_Write<u8> for File
{
    type Error = std::io::Error;

    fn write(&mut self, word: u8) -> nb::Result<(), Self::Error> {
        match self.0.write(&[word]) {
            Ok(1) => Ok(()),
            Ok(_) => Err(nb::Error::Other(std::io::Error::from(std::io::ErrorKind::Other))),
            Err(err) => Err(nb::Error::Other(err))
        }
    }

    fn flush(&mut self) -> nb::Result<(), Self::Error> {
        match self.0.flush() {
            Ok(()) => Ok(()),
            Err(err) => Err(nb::Error::Other(err))
        }
    }
}


fn main() {

    let printer_handle = match std::fs::File::open("/dev/usb/lp0") {
        Ok(file) => file,
        Err(err) => panic!("Unable to talk to printer: {}", err),
    };

    let mut printer = ThermalPrinter::new(File(printer_handle));

    //printer.write("Hello World!"); // why doesn't this exist?!
    printer.feed_n(3).unwrap();
    printer.flush().unwrap();

    println!("Hello, world!");
}
