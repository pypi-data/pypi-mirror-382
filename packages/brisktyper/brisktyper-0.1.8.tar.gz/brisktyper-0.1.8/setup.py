#!/usr/bin/env python3

import collections
import csv
import datetime
import gzip
import os
import shutil
import sys
import urllib.request
import xml.etree.ElementTree as etree

import setuptools
from setuptools.command.build_py import build_py as _build_py


class build_py(_build_py):
    """A modified `build_py` command to download data files.
    """

    def run(self):
        # build the rest of the package as normal
        _build_py.run(self)

        # get the path where to download the files
        brisktyper_path = os.path.join(self.build_lib, "brisktyper")

        # download NCBI PubMLST database
        self.download_pubmlst(brisktyper_path)

        # download genome files for each databases
        for subset in ("species", "subspecies", "geneflow", "typestrains", "cytotoxicity"):
            db = os.path.join(brisktyper_path, "seq_ani_db", subset, "{}.tsv".format(subset))
            self.download_genomes(brisktyper_path, db, subset)

    def download(self, url, dest, append=False, decompress=False):
        print("downloading {!r} to {!r}".format(url, dest))
        self.mkpath(os.path.dirname(dest))
        try:
            with urllib.request.urlopen(url) as req:
                if decompress:
                    req = gzip.GzipFile(fileobj=req, mode="rb")
                with open(dest, "ab" if append else "wb") as dst:
                    shutil.copyfileobj(req, dst)
        except:
            if os.path.exists(dest):
                os.remove(dest)
            raise

    def download_pubmlst(self, brisktyper_path):
        # write a timestamp to know when the DB was built in future runs
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        print("downloading most recent PubMLST database at {}".format(now))
        with open(os.path.join(brisktyper_path, "seq_mlst_db", "timestamp.txt"), "w") as f:
            f.write("{}\n".format(now))

        with urllib.request.urlopen("https://pubmlst.org/data/dbases.xml") as req:
            tree = etree.parse(req)
            parent = next(e for e in tree.iter("species") if e.text.strip() == "Bacillus cereus")
            urls = (e.text for e in parent.iter("url"))

        for url in urls:
            if "alleles_fasta" in url:
                self.download(url, os.path.join(brisktyper_path, "seq_mlst_db", "mlst.fas"), append=True)
            elif "profiles_csv" in url:
                self.download(url, os.path.join(brisktyper_path, "seq_mlst_db", "bcereus.txt"))

    def download_genomes(self, brisktyper_path, genome_list, ani_directory):
        with open(genome_list) as genomes:
            reader = csv.reader(genomes, dialect="excel-tab")

            header = next(reader)
            id_col = header.index("id")
            url_col = header.index("url")

            for row in reader:
                gfile = os.path.join(brisktyper_path, "seq_ani_db", ani_directory, row[id_col])
                if not os.path.isfile(gfile):
                    self.download(url=row[url_col], dest=gfile)


setuptools.setup(cmdclass={"build_py": build_py})
