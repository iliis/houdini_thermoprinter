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
        //match std::io::Write::write_all(&mut self.0, &[word]) { // without use std::io::Write
        match self.0.write_all(&[word]) {
            Ok(()) => Ok(()),
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

    let printer_handle = match std::fs::OpenOptions::new().write(true).open("/dev/usb/lp0") {
        Ok(file) => file,
        Err(err) => panic!("Unable to talk to printer: {}", err),
    };

    let mut printer = ThermalPrinter::new(File(printer_handle));

    printer.configure(80, 90, 160).unwrap(); // looks nice

    //printer.write("Hello World!"); // why doesn't this exist?!
    //printer.run_test().expect("selftest failed!");
    //printer.feed_n(3).expect("feed failed!");

/*
    for dot in vec![1,10,20,40,80,120,160,200,255] {
    //for dot in vec![1,10,20,70,75,80,85,90,95,100,105,110,115,120,125,130,70,120,20,120] {
        printer.configure(80, 80, dot).unwrap();
        //std::thread::sleep(std::time::Duration::from_millis(200));
        printer.write_all(format!("### 80/80/interval: {}\n", dot).as_bytes()).unwrap();
        //write!(&mut printer, "dot time: {}\n", dot).unwrap();
    }
    */
    printer.run_test().unwrap();

    printer.feed_n(10).unwrap();
    printer.flush().unwrap();
}
