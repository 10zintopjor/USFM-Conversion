import re
from pathlib import Path
import math
from openpecha.alignment.exporter import Exporter


class UsfmExporter(Exporter):

    def __init__(self, alignment_path) -> None:
        super().__init__(alignment_path)
        self.verse_no = 0

    def get_seg_ann(self, segment_id, segment_annotations):
        """"Return Segment Annotation of Segment id

        Args:
            segment_id(str): segment uuid
            segment_annotation(dict): segment annotation

        Returns:
            {dict}: Segment Annotation of Segment id
        """

        for seg_id, item in segment_annotations.items():
            if seg_id == segment_id:
                return item

    def write_file(self, segments):

        commentary_dir = segments["commentary_dir"]
        root_dir = segments["root_dir"]

        with open(commentary_dir, "a") as g:
            if self.verse_no < 1:
                g.write(r"\mt " + segments["commentary_text"] + "\n")
                g.write(r"\b" + "\n")
                self.verse_no += 0.5
            else:
                g.write(r"\v " + str(math.floor(self.verse_no)) + " " + segments["commentary_text"] + "\n")
                self.verse_no += 0.5
                g.write(r"\q" + "\n")
                g.write(r"\b" + "\n")

        with open(root_dir, "a") as f:
            if self.verse_no < 1:
                f.write(r"\mt " + segments["root_text"] + "\n")
                f.write(r"\b" + "\n")
                self.verse_no += 0.5
            else:
                lines = segments["root_text"].splitlines()
                for index, line in enumerate(lines):
                    if index == 0:
                        f.write(r"\v " + str(math.floor(self.verse_no)) + " " + line + "\n")
                        self.verse_no += 0.5

                    else:
                        f.write(r"\q1 " + line + "\n")

                f.write(r"\b" + "\n")
                f.write(r"\qd " + segments["commentary_text"] + "\n")
                f.write(r"\q" + "\n")
                f.write(r"\b" + "\n")

    def write_usfm(self, seg_pairs, output_path):
        """Writes segement text into Usfm

        Args:
            source_id(str):pecha uuid
            segment_id(str):segment uuid
            output_path(str):Output directory to write the files
        """
        segments = {}
        for item, value in seg_pairs.items():
            if item == self.src_id:
                segment_annotations = self.get_segment_layer(self.src_id, self.src_pecha_path)
                seg_ann = self.get_seg_ann(value, segment_annotations)
                directory = f"{output_path}/C01/root.txt"
                seg_text = self.get_segment(seg_ann, self.src_base_text)
                segments["root_dir"] = directory
                segments["root_text"] = seg_text
            else:
                segment_annotations = self.get_segment_layer(self.tar_id, self.tar_pecha_path)
                seg_ann = self.get_seg_ann(value, segment_annotations)
                directory = f"{output_path}/C02/commentary.txt"
                seg_text = self.get_segment(seg_ann, self.tar_base_text)
                segments["commentary_dir"] = directory
                segments["commentary_text"] = seg_text

        self.write_file(segments)

    def export(self, output_path):
        """Exports the Usfm files to output_path

        Args:
            output_path(str):Output directory to write the files

        """

        segment_srcs = self.alignment.get("segment_sources", {})


        for seg_src_id, seg_src in segment_srcs.items():
            if seg_src.get("relation", "") == "root":
                self.src_id = seg_src_id
            else:
                self.tar_id = seg_src_id

        self.src_pecha_path = Path("./chojuk/4c3212759b4a4d32a5303ede4fc84b4b")
        self.tar_pecha_path = Path("./chojuk/6d68bb52befb438e8a1d9c60f791575b")
        self.src_base_text = self.get_base_layer(self.src_id, self.src_pecha_path)
        self.tar_base_text = self.get_base_layer(self.tar_id, self.tar_pecha_path)

        segment_pairs = self.alignment.get("segment_pairs", {})

        for seg_pair_id, seg_pairs in segment_pairs.items():
            self.write_usfm(seg_pairs, output_path)
