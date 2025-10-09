#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#@created: 25.03.2023
#@author: Aleksey Komissarov
#@contact: ad3002@gmail.com
""" Fast quast for large assemblies. """

import argparse
import os
import logging
import sys
import gzip
from typing import TextIO, Union

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

report_keys = [
    'Assembly',
    '# contigs (>= 0 bp)',
    '# contigs (>= 1000 bp)',
    '# contigs (>= 5000 bp)',
    '# contigs (>= 10000 bp)',
    '# contigs (>= 25000 bp)',
    '# contigs (>= 50000 bp)',
    '# contigs (>= 500000 bp)',
    '# contigs (>= 1000000 bp)',
    '# contigs (>= 10000000 bp)',
    'Total length (>= 0 bp)',
    'Total length (>= 1000 bp)',
    'Total length (>= 5000 bp)',
    'Total length (>= 10000 bp)',
    'Total length (>= 25000 bp)',
    'Total length (>= 50000 bp)',
    'Total length (>= 500000 bp)',
    'Total length (>= 1000000 bp)',
    'Total length (>= 10000000 bp)',
    '# contigs',
    'Largest contig',
    'Total length',
    'N50',
    'L50',
    'N75',
    'L75',
    "# N's per 100 kbp",
    '# gaps',
]

def open_file(file_path) -> Union[TextIO, gzip.GzipFile]:
    """Open a file and return a file object."""
    if file_path.endswith('.gz'):
        return gzip.open(file_path, "rt", encoding="utf8")
    else:
        return open(file_path, "r", encoding="utf8")


def check_input_output_files(files_to_process, output_dir):
    """Check if input files exist and if output files can be created."""
    for file_name in files_to_process:
        if not os.path.isfile(file_name):
            logging.error(f"File {file_name} not found.")
            sys.exit(1)
    if output_dir and not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    for file_name in files_to_process:
        output_file = os.path.splitext(file_name)[0] + ".quast"
        if output_dir:
            output_file = os.path.join(output_dir, os.path.basename(output_file))
        try:
            with open(output_file, "w") as f:
                pass
        except Exception as e:
            logging.error(f"Cannot create output file {output_file}: {e}")
            sys.exit(1)
    return True


def check_input_extensions(files_to_process, allowed_extensions):
    """Check if input files have the correct extensions."""
    for file_name in files_to_process:
        if not any(file_name.endswith(ext) for ext in allowed_extensions):
            logging.error(f"File {file_name} has an invalid extension.")
            sys.exit(1)
    return True


def iter_fasta_file(fasta_file_name, split_scaffolds):
    """Iterate over a fasta file and yield the sequence length and a number of N.
    If split_scaffolds is True, the sequence length will be split on Ns.
    """
    with open_file(fasta_file_name) as input_file:
        header = False
        seq_length = 0
        N = 0
        for line in input_file:
            line = line.strip()
            N += line.count("N")
            if split_scaffolds:
                lines = line.split("N")
                lines_len = len(lines)
                if lines_len > 1:
                    for subline in lines:
                        if not subline:
                            continue
                        seq_length += len(subline)
                        yield seq_length, 0
                        seq_length = 0
            if not line:
                break
            if line.startswith(">"):
                if header:
                    yield seq_length, N
                    seq_length = 0
                header = True
            else:
                seq_length += len(line)
        if header:
            yield seq_length, N

def count_gaps_in_fasta_file(fasta_file_name):
    """Count gaps in a fasta file. If gaps in the start or end of the sequence we count them too."""
    logging.info("Computing gaps in fasta file...")
    gaps = 0
    in_gaps = False

    with open(fasta_file_name, 'r') as input_file:
        for line in input_file:
            if line.startswith('>'):
                continue
            line = line.strip()
            for c in line:
                if c == 'N':
                    if not in_gaps:
                        in_gaps = True
                        gaps += 1
                else:
                    in_gaps = False

    logging.info("Gaps: %d", gaps)
    return gaps

def iter_fastq_file(file_name, split_scaffolds=False):
    """Iterate over a FASTQ file and yield sequence length and number of N's."""
    with open_file(file_name) as f:
        while True:
            # Read the next four lines from the file
            header = f.readline().strip()
            seq = f.readline().strip()
            plus = f.readline().strip()
            qual = f.readline().strip()

            # If any of the lines are empty, we've reached the end of the file
            if not header or not seq or not plus or not qual:
                break

            # Calculate the sequence length and number of N's
            seq_length = len(seq)
            n_nucleotides = seq.count('N')

            # If split_scaffolds is True, split the sequence into scaffolds
            if split_scaffolds:
                scaffolds = seq.split('N' * 10)
                for scaffold in scaffolds:
                    yield len(scaffold), scaffold.count('N')
            else:
                yield seq_length, n_nucleotides

def print_available_extensions(extension_to_function):
    """Print the available extensions from extension_to_function."""
    extensions = list(extension_to_function.keys())
    logging.error(f"Available file extensions: {', '.join(extensions)}")

def get_function_for_extension(file_name, extension_to_function):
    """Run a function based on the file extension of the given file name."""
    file_extension = file_name.split(".")[-1]
    if file_extension == "gz":
        file_extension = file_name.split(".")[-2] + ".gz"
    if file_extension in extension_to_function:
        return extension_to_function[file_extension]
    else:
        print_available_extensions(extension_to_function)
        logging.error(f"No function found for file extension {file_extension}")
        sys.exit(1)

def get_n50_and_l50(contig_lengths):
    """Return the N50 and L50 for a list of contig lengths."""
    total_length = sum(contig_lengths)
    target_length = total_length / 2
    sorted_lengths = sorted(contig_lengths, reverse=True)
    current_length = 0
    for i, length in enumerate(sorted_lengths):
        current_length += length
        if current_length >= target_length:
            return length, i + 1
    return 0, 0

def get_n_and_l_for_fraction(contig_lengths, fraction):
    """Return the N and L for a given fraction of the total assembly length."""
    total_length = sum(contig_lengths)
    target_length = total_length * fraction
    sorted_lengths = sorted(contig_lengths, reverse=True)
    current_length = 0
    for i, length in enumerate(sorted_lengths):
        current_length += length
        if current_length >= target_length:
            return length, i + 1
    return 0, 0

def calculate_n_per_100kbp(total_length, total_n):
    """Return the number of Ns per 100 kbp."""
    return (total_n / total_length) * 100000

def count_n_bases(length):
    """Return the number of N bases in a sequence."""
    return length.count('N') if isinstance(length, str) else 0

def generate_data_dict(contig_lengths, assembly_name, total_n):
    """Return a dictionary of data for the report."""
    n_contigs = len(contig_lengths)
    total_length = sum(contig_lengths)
    n_1000 = sum(1 for x in contig_lengths if x >= 1000)
    n_5000 = sum(1 for x in contig_lengths if x >= 5000)
    n_10000 = sum(1 for x in contig_lengths if x >= 10000)
    n_25000 = sum(1 for x in contig_lengths if x >= 25000)
    n_50000 = sum(1 for x in contig_lengths if x >= 50000)
    n_500000 = sum(1 for x in contig_lengths if x >= 500000)
    n_1000000 = sum(1 for x in contig_lengths if x >= 1000000)
    n_10000000 = sum(1 for x in contig_lengths if x >= 10000000)
    total_length_1000 = sum(x for x in contig_lengths if x >= 1000)
    total_length_5000 = sum(x for x in contig_lengths if x >= 5000)
    total_length_10000 = sum(x for x in contig_lengths if x >= 10000)
    total_length_25000 = sum(x for x in contig_lengths if x >= 25000)
    total_length_50000 = sum(x for x in contig_lengths if x >= 50000)
    total_length_500000 = sum(x for x in contig_lengths if x >= 500000)
    total_length_1000000 = sum(x for x in contig_lengths if x >= 1000000)
    total_length_10000000 = sum(x for x in contig_lengths if x >= 10000000)
    largest_contig = max(contig_lengths)
    n50, l50 = get_n50_and_l50(contig_lengths)
    n75, l75 = get_n_and_l_for_fraction(contig_lengths, 0.75)
    n_per_100kbp = round(calculate_n_per_100kbp(total_length, total_n), 2)

    report_dict = {
        'Assembly': assembly_name,
        '# contigs (>= 0 bp)': n_contigs,
        '# contigs (>= 1000 bp)': n_1000,
        '# contigs (>= 5000 bp)': n_5000,
        '# contigs (>= 10000 bp)': n_10000,
        '# contigs (>= 25000 bp)': n_25000,
        '# contigs (>= 50000 bp)': n_50000,
        '# contigs (>= 500000 bp)': n_500000,
        '# contigs (>= 1000000 bp)': n_1000000,
        '# contigs (>= 10000000 bp)': n_10000000,
        'Total length (>= 0 bp)': total_length,
        'Total length (>= 1000 bp)': total_length_1000,
        'Total length (>= 5000 bp)': total_length_5000,
        'Total length (>= 10000 bp)': total_length_10000,
        'Total length (>= 25000 bp)': total_length_25000,
        'Total length (>= 50000 bp)': total_length_50000,
        'Total length (>= 500000 bp)': total_length_500000,
        'Total length (>= 1000000 bp)': total_length_1000000,
        'Total length (>= 10000000 bp)': total_length_10000000,
        '# contigs': n_contigs,
        'Largest contig': largest_contig,
        'Total length': total_length,
        'N50': n50,
        'L50': l50,
        'N75': n75,
        'L75': l75,
        '# N\'s per 100 kbp': n_per_100kbp
    }

    return report_dict


def generate_combined_report(results_data, tsv_report=False):
    """Return a string of the combined report."""
    lines = []
    max_key_length = max(len(key) for key in report_keys)
    for key in report_keys:
        if key not in results_data[0]:
            continue
        lines.append([key.ljust(max_key_length + 2)])

    max_length_of_name = max(len(x) for x in results_data)
    max_adjusted_length = max_length_of_name + 18

    for report in results_data:
        max_adjusted_length = max(len(str(x)) for x in report.values()) + 4
        for i, key in enumerate(report_keys):
            if key not in report:
                continue
            lines[i].append(str(report[key]).ljust(max_adjusted_length))

    if tsv_report:
        return "\n".join(["\t".join([y.strip() for y in x]) for x in lines])
    return "\n".join(["".join(x) for x in lines])


def inter_assembly_summary(assembly_list):
    """Return a string of the inter-assembly summary."""
    for i, assembly in enumerate(assembly_list, start=1):
        n_nucleotides = assembly["# N's per 100 kbp"]
        assembly_name = assembly['Assembly']
        n50 = assembly['N50']
        l50 = assembly['L50']
        total_length = assembly['Total length']
        output = "    %s  %s, N50 = %s, L50 = %s, Total length = %s, # N's per 100 kbp = %s" % (i, assembly_name, n50, l50, total_length, n_nucleotides)
        if "gaps" in assembly:
            output += ", # gaps = %s" % assembly["gaps"]
        yield output


def main():
    """Run the main program."""
    parser = argparse.ArgumentParser(description='Fast and simple Quality Assessment Tool for Genome Assemblies or Long Reads')

    parser.add_argument('files_with_contigs', nargs='+', help='List of files with contigs in fasta or fastq format (raw or gzipped)')
    parser.add_argument('-o', '--output-dir', default=None, help='Directory to store all result files [default: replace file extension with quast extension]')
    parser.add_argument('-s', '--split-scaffolds', action='store_true', help='Split assemblies by continuous fragments of N\'s and add such "contigs" to the comparison [default: False]', default=False)
    parser.add_argument('-m', '--min-contig', type=int, default=1, help='Lower threshold for contig length [default: 1]')
    parser.add_argument('-l', '--labels', default=None, help='Names of assemblies to use in reports, comma-separated. If contain spaces, use quotes')
    parser.add_argument('--gaps', default=False, help='Count gaps in contigs, please, note that FastQust will run much slower with this option [default: false]', action='store_true')
    parser.add_argument('--tsv', default=False, help='Save report in TSV format to the specified file [default: false]', action='store_true')

    args = parser.parse_args()
    files_to_process = args.files_with_contigs
    split_scaffolds = args.split_scaffolds
    labels = args.labels
    min_contig = int(args.min_contig)
    output_dir = args.output_dir
    tsv_report = args.tsv
    compute_gaps = args.gaps

    extension_to_function = {
        "fasta": iter_fasta_file,
        "fasta.gz": iter_fasta_file,
        "fa": iter_fasta_file,
        "fa.gz": iter_fasta_file,
        "fna": iter_fasta_file,
        "fna.gz": iter_fasta_file,
        "fastq": iter_fastq_file,
        "fq": iter_fastq_file,
        "fastq.gz": iter_fastq_file,
        "fq.gz": iter_fastq_file,
    }

    if labels:
        labels = [label.strip() for label in labels.split(",")]
        if len(labels) != len(files_to_process):
            logging.error("number of labels should be equal to number of files")
            sys.exit(1)
    else:
        labels = [
            os.path.splitext(os.path.basename(file_path))[0] for file_path in files_to_process]

    check_input_output_files(files_to_process, output_dir)
    check_input_extensions(files_to_process, extension_to_function)

    output_files = []
    for file_name in files_to_process:
        logging.info("Processing file %s" % file_name)
        output_file = os.path.splitext(file_name)[0] + ".quast"
        if output_dir:
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir)
            output_file = os.path.join(output_dir, os.path.basename(output_file))
        output_files.append(output_file)

    results_data = []
    for i, file_name in enumerate(files_to_process):
        sizes = []
        total_n = 0
        func = get_function_for_extension(file_name, extension_to_function)

        for seq_length, n_nucleotides in func(file_name, split_scaffolds):
            if seq_length >= min_contig:
                sizes.append(seq_length)
                total_n += n_nucleotides
        data_dict = generate_data_dict(sizes, labels[i], total_n)
        if compute_gaps:
            gaps = count_gaps_in_fasta_file(file_name)
            data_dict['# gaps'] = gaps
        results_data.append(data_dict)

    report_table = generate_combined_report(results_data, tsv_report=tsv_report)

    for output_file in output_files:
        with open(output_file, "w", encoding="utf8") as fw:
            fw.write(report_table)

    for summary in inter_assembly_summary(results_data):
        print(summary)


if __name__ == "__main__":
    main()
