use std::fs::{self, File};
use std::io::{self, Seek, SeekFrom, Write};
use std::process;

use clap::{Parser, Subcommand};
use prettytable::{Attr, Cell, Row, Table};

use fw_file::dcm::{DeidProfile, parse_header, read_until_pixels};

#[derive(Parser)]
#[command(name = "dicom-tool")]
#[command(author, version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    GetDcmMeta {
        #[arg(required = true)]
        file_path: String,

        #[arg(required = true)]
        tags: Vec<String>,
    },
    DeidDcm {
        #[arg(required = true)]
        file_path: String,

        #[arg(required = true)]
        profile_path: String,
    },
}

fn main() -> io::Result<()> {
    let cli = Cli::parse();

    match &cli.command {
        Commands::GetDcmMeta { file_path, tags } => {
            let start_time = std::time::Instant::now();
            println!("Running 'get-dcm-meta' on: {}", file_path);
            let mut file = File::open(file_path).expect("Could not open file");
            let bytes =
                read_until_pixels(&mut file, &[], None).expect("Failed to read DICOM metadata");
            let tag_slices: Vec<&str> = tags.iter().map(|s| s.as_str()).collect();
            match parse_header(&bytes, &tag_slices) {
                Ok(meta) => {
                    if meta.is_empty() {
                        println!("\nNo metadata found for the specified tags.");
                        return Ok(());
                    }

                    println!("\nParsed metadata:");
                    let mut table = Table::new();

                    table.add_row(Row::new(vec![
                        Cell::new("Tag").with_style(Attr::Bold),
                        Cell::new("Value").with_style(Attr::Bold),
                    ]));

                    for (key, value) in meta {
                        table.add_row(Row::new(vec![
                            Cell::new(&key),
                            Cell::new(&value.to_string().trim_matches('"')),
                        ]));
                    }

                    table.printstd();
                }
                Err(err) => {
                    eprintln!("Error parsing DICOM: {err}");
                    process::exit(1);
                }
            }
            println!("\n'get-dcm-meta' finished in {:?}", start_time.elapsed());
        }

        Commands::DeidDcm {
            file_path,
            profile_path,
        } => {
            let start_time = std::time::Instant::now();

            println!("Running 'deid-dcm' on: {}", file_path);
            println!("Using profile: {}", profile_path);

            let temp_file_path_str = format!("{}.tmp", file_path);

            {
                let mut source_file = File::open(file_path)?;
                let mut temp_file = File::create(&temp_file_path_str)?;
                let dcm_header_bytes = read_until_pixels(&mut source_file, &[], None).unwrap();
                let pixel_data_start = dcm_header_bytes.len();
                let yaml_data =
                    fs::read_to_string(profile_path).expect("Could not read de-id profile file");
                let profile =
                    DeidProfile::from_yaml(&yaml_data).expect("Failed to parse de-id profile");
                let deidentified_header = profile
                    .deid_dcm(&dcm_header_bytes)
                    .expect("De-identification process failed");

                temp_file.write_all(&deidentified_header)?;

                println!("Streaming pixel data...");
                source_file.seek(SeekFrom::Start(pixel_data_start as u64))?;
                io::copy(&mut source_file, &mut temp_file)?;
            }

            fs::rename(&temp_file_path_str, file_path)?;

            println!(
                "Successfully de-identified and saved file to: {}",
                file_path
            );
            println!("'deid-dcm' finished in {:?}", start_time.elapsed());
        }
    }

    Ok(())
}
