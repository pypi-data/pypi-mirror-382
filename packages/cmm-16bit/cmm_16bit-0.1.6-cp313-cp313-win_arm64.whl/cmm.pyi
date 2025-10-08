"""

        Color Management Module
        -----------------------

        .. currentmodule:: cmm

        .. autosummary::
           :toctree: _generate
    
"""
from __future__ import annotations
import numpy
import typing
__all__ = ['INTENT_ABSOLUTE_COLORIMETRIC', 'INTENT_PERCEPTUAL', 'INTENT_RELATIVE_COLORIMETRIC', 'INTENT_SATURATION', 'PT_ANY', 'PT_CMY', 'PT_CMYK', 'PT_GRAY', 'PT_HLS', 'PT_HSV', 'PT_Lab', 'PT_RGB', 'PT_XYZ', 'PT_YCbCr', 'PT_YUV', 'PT_YUVK', 'PT_Yxy', 'add_lut16', 'close_profile', 'cmsERROR_ALREADY_DEFINED', 'cmsERROR_BAD_SIGNATURE', 'cmsERROR_COLORSPACE_CHECK', 'cmsERROR_CORRUPTION_DETECTED', 'cmsERROR_FILE', 'cmsERROR_INTERNAL', 'cmsERROR_NOT_SUITABLE', 'cmsERROR_NULL', 'cmsERROR_RANGE', 'cmsERROR_READ', 'cmsERROR_SEEK', 'cmsERROR_UNDEFINED', 'cmsERROR_UNKNOWN_EXTENSION', 'cmsERROR_WRITE', 'cmsFLAGS_BLACKPOINTCOMPENSATION', 'cmsFLAGS_GAMUTCHECK', 'cmsFLAGS_HIGHRESPRECALC', 'cmsFLAGS_KEEP_SEQUENCE', 'cmsFLAGS_NOOPTIMIZE', 'cmsFLAGS_NULLTRANSFORM', 'cmsFLAGS_SOFTPROOFING', 'cmsSig10colorData', 'cmsSig11colorData', 'cmsSig12colorData', 'cmsSig13colorData', 'cmsSig14colorData', 'cmsSig15colorData', 'cmsSig1colorData', 'cmsSig2colorData', 'cmsSig3colorData', 'cmsSig4colorData', 'cmsSig5colorData', 'cmsSig6colorData', 'cmsSig7colorData', 'cmsSig8colorData', 'cmsSig9colorData', 'cmsSigAbstractClass', 'cmsSigCmyData', 'cmsSigCmykData', 'cmsSigColorSpaceClass', 'cmsSigDisplayClass', 'cmsSigGrayData', 'cmsSigHlsData', 'cmsSigHsvData', 'cmsSigInputClass', 'cmsSigLabData', 'cmsSigLinkClass', 'cmsSigLuvData', 'cmsSigLuvKData', 'cmsSigMCH1Data', 'cmsSigMCH2Data', 'cmsSigMCH3Data', 'cmsSigMCH4Data', 'cmsSigMCH5Data', 'cmsSigMCH6Data', 'cmsSigMCH7Data', 'cmsSigMCH8Data', 'cmsSigMCH9Data', 'cmsSigMCHAData', 'cmsSigMCHBData', 'cmsSigMCHCData', 'cmsSigMCHDData', 'cmsSigMCHEData', 'cmsSigMCHFData', 'cmsSigNamedColorClass', 'cmsSigNamedData', 'cmsSigOutputClass', 'cmsSigRgbData', 'cmsSigXYZData', 'cmsSigYCbCrData', 'cmsSigYxyData', 'create_partial_profile', 'create_proofing_transform', 'create_srgb_profile', 'create_transform', 'delete_transform', 'do_transform_16_16', 'do_transform_16_8', 'do_transform_8_16', 'do_transform_8_8', 'dump_profile', 'eval_lut16', 'eval_pre_table', 'get_available_b2an_list', 'get_color_space', 'get_device_class', 'get_profile_description', 'get_transform_formatter', 'link_tag', 'open_profile_from_mem', 'set_alarm_codes', 'set_log_error_handler', 'unset_log_error_handler']
def add_lut16(hprofile: capsule, tag: str, n_out_ch: int, clut: numpy.ndarray[numpy.uint16], pre_table: numpy.ndarray[numpy.uint16], post_table: numpy.ndarray[numpy.uint16]) -> int:
    """
    		Adds a lut16 to a profile.
    
    		Parameters
    		----------
    		hprofile: PyCapsule
    			Profile handle
    		tag: str
    			AnBm, BnAm, or 'gamt'
    		n_out_ch: int
    			Number of output channel
    		clut: ndarray[uint16]
    			CLUT
    		pre_table: ndarray[uint16]
    			Tone curve before CLUT stage
    		post_table: ndarray[uint16]
    			Tone curve after CLUT stage
    
    		Returns
    		-------
    		int
    			0 if fail
    """
def close_profile(hprofile: capsule) -> None:
    """
    		Closes ICC profile.
    
    		Parameters
    		----------
    		hp: PyCapsule
    			Profile handle
    """
def create_partial_profile(desc: str, cprt: str, is_glossy: bool, wtpt: numpy.ndarray[numpy.float64]) -> capsule:
    """
    		Creates a partial profile. Partial profile should be completed before dump_profile().
    
    		Parameters
    		----------
    		desc: str
    			Description string
    		cprt: str
    			Copyright string
    		is_glossy: bool
    		wtpt: ndarray[float64]
    			XYZ values of white point
    
    		Returns
    		-------
    		PyCapsule
    			Profile handle
    """
def create_proofing_transform(src_hp: capsule, src_format: int, trg_hp: capsule, trg_format: int, proof_hp: capsule, intent: int, proof_intent: int, flags: int) -> capsule:
    """
    		Creates soft proof transform.
    
    		Parameters
    		----------
    		src_hp: PyCapsule
    			Profile handle of source
    
    		src_format: int
    			Source format
    
    		trg_hp: PyCapsule
    			Profile handle of target
    
    		trg_format: int
    			Target format
    
    		proof_hp: PyCapsule
    			Profile handle to proof
    
    		intent: int
    			Color conversion intent
    			INTENT_PERCEPTUAL				0
    			INTENT_RELATIVE_COLORIMETRIC	1
    			INTENT_SATURATION				2
    			INTENT_ABSOLUTE_COLORIMETRIC	3
    
    		flags: int
    			Conversion flag
    			cmsFLAGS_BLACKPOINTCOMPENSATION	0x2000
    			cmsFLAGS_HIGHRESPRECALC			0x0400
    			cmsFLAGS_NULLTRANSFORM			0x0200
    			cmsFLAGS_NOOPTIMIZE				0x0100
    			cmsFLAGS_KEEP_SEQUENCE			0x0080
    			cmsFLAGS_GAMUTCHECK				0x1000
    			cmsFLAGS_SOFTPROOFING			0x4000
    
    		Returns
    		-------
    		PyCapsule
    			Transform handle
    """
def create_srgb_profile() -> capsule:
    """
    		Creates sRGB profile.
    """
def create_transform(src_hp: capsule, src_format: int, trg_hp: capsule, trg_format: int, intent: int, flags: int) -> capsule:
    """
    		Creates transform.
    
    		Parameters
    		----------
    		src_hp: PyCapsule
    			Profile handle of source
    
    		src_format: int
    			Source format
    
    		trg_hp: PyCapsule
    			Profile handle of target
    
    		trg_format: int
    			Target format
    
    		intent: int
    			Color conversion intent
    			INTENT_PERCEPTUAL				0
    			INTENT_RELATIVE_COLORIMETRIC	1
    			INTENT_SATURATION				2
    			INTENT_ABSOLUTE_COLORIMETRIC	3
    
    		flags: int
    			Conversion flag
    			cmsFLAGS_BLACKPOINTCOMPENSATION	0x2000
    			cmsFLAGS_HIGHRESPRECALC			0x0400
    			cmsFLAGS_NULLTRANSFORM			0x0200
    			cmsFLAGS_NOOPTIMIZE				0x0100
    			cmsFLAGS_KEEP_SEQUENCE			0x0080
    
    		Returns
    		-------
    		PyCapsule
    			Transform handle
    """
def delete_transform(htransform: capsule) -> None:
    """
    		Deletes transform.
    
    		Parameters
    		----------
    		htransform: PyCapsule
    			Transform handle
    """
def do_transform_16_16(htransform: capsule, input_buf: numpy.ndarray[numpy.uint16], output_buf: numpy.ndarray[numpy.uint16], num_pixel: int) -> None:
    """
    		Does transform from uint16 to uint16.
    
    		Parameters
    		----------
    		htransform: PyCapsule
    			Transform handle
    
    		input_buf: ndarray[uint16]
    		output_buf: ndarray[uint16]
    		num_pixel: int
    """
def do_transform_16_8(htransform: capsule, input_buf: numpy.ndarray[numpy.uint16], output_buf: numpy.ndarray[numpy.uint8], num_pixel: int) -> None:
    """
    		Does transform from uint16 to uint8.
    
    		Parameters
    		----------
    		htransform: PyCapsule
    			Transform handle
    
    		input_buf: ndarray[uint16]
    		output_buf: ndarray[uint8]
    		num_pixel: int
    """
def do_transform_8_16(htransform: capsule, input_buf: numpy.ndarray[numpy.uint8], output_buf: numpy.ndarray[numpy.uint16], num_pixel: int) -> None:
    """
    		Does transform from uint8 to uint16.
    
    		Parameters
    		----------
    		htransform: PyCapsule
    			Transform handle
    
    		input_buf: ndarray[uint8]
    		output_buf: ndarray[uint16]
    		num_pixel: int
    """
def do_transform_8_8(htransform: capsule, input_buf: numpy.ndarray[numpy.uint8], output_buf: numpy.ndarray[numpy.uint8], num_pixel: int) -> None:
    """
    		Does transform from uint8 to uint8.
    
    		Parameters
    		----------
    		htransform: PyCapsule
    			Transform handle
    
    		input_buf: ndarray[uint8]
    		output_buf: ndarray[uint8]
    		num_pixel: int
    """
def dump_profile(hprofile: capsule) -> bytes:
    """
    		Dumps a profile.
    
    		Parameters
    		----------
    		hprofile: PyCapsule
    			Profile handle
    
    		Returns
    		-------
    		bytes
    			Profile content
    """
def eval_lut16(hprofile: capsule, tag: str, input_array: numpy.ndarray[numpy.uint16], output_array: numpy.ndarray[numpy.uint16]) -> int:
    """
    		Evaluates lut16 by input_array.
    
    		Parameters
    		----------
    		hprofile: PyCapsule
    			Profile handle
    		tag: str
    			AnBm, BnAm, or 'gamt'
    		input_array: ndarray[uint16]
    		output_array: ndarray[uint16]
    
    		Returns
    		-------
    		int
    			0 if fail
    """
def eval_pre_table(hprofile: capsule, tag: str, input_array: numpy.ndarray[numpy.uint16], output_array: numpy.ndarray[numpy.uint16]) -> int:
    """
    		Evaluates pre_table of the tag by input_array.
    
    		Parameters
    		----------
    		hprofile: PyCapsule
    			Profile handle
    		tag: str
    			AnBm, BnAm, or 'gamt'
    		input_array: ndarray[uint16]
    		output_array: ndarray[uint16]
    
    		Returns
    		-------
    		int
    			0 if fail
    """
def get_available_b2an_list(hprofile: capsule) -> list[str]:
    """
    		Gets available B2An list
    
    		Parameters
    		----------
    		hp: PyCapsule
    			Profile handle
    
    		Returns
    		-------
    		[str]
    			'B2A0', 'B2A1', and/or 'B2A2'
    """
def get_color_space(hprofile: capsule) -> int:
    """
    		Gets color space.
    
    		Parameters
    		----------
    		hp: PyCapsule
    			Profile handle
    
    		Returns
    		-------
    		int
    			cmsSigXYZData 0x58595A20 'XYZ '
    			cmsSigLabData 0x4C616220 'Lab '
    			cmsSigLuvData 0x4C757620 'Luv '
    			cmsSigYCbCrData 0x59436272 'YCbr'
    			cmsSigYxyData 0x59787920 'Yxy '
    			cmsSigRgbData 0x52474220 'RGB '
    			cmsSigGrayData 0x47524159 'GRAY'
    			cmsSigHsvData 0x48535620 'HSV '
    			cmsSigHlsData 0x484C5320 'HLS '
    			cmsSigCmykData 0x434D594B 'CMYK'
    			cmsSigCmyData 0x434D5920 'CMY '
    			cmsSigMCH1Data 0x4D434831 'MCH1'
    			cmsSigMCH2Data 0x4D434832 'MCH2'
    			cmsSigMCH3Data 0x4D434833 'MCH3'
    			cmsSigMCH4Data 0x4D434834 'MCH4'
    			cmsSigMCH5Data 0x4D434835 'MCH5'
    			cmsSigMCH6Data 0x4D434836 'MCH6'
    			cmsSigMCH7Data 0x4D434837 'MCH7'
    			cmsSigMCH8Data 0x4D434838 'MCH8'
    			cmsSigMCH9Data 0x4D434839 'MCH9'
    			cmsSigMCHAData 0x4D43483A 'MCHA'
    			cmsSigMCHBData 0x4D43483B 'MCHB'
    			cmsSigMCHCData 0x4D43483C 'MCHC'
    			cmsSigMCHDData 0x4D43483D 'MCHD'
    			cmsSigMCHEData 0x4D43483E 'MCHE'
    			cmsSigMCHFData 0x4D43483F 'MCHF'
    			cmsSigNamedData 0x6e6d636c 'nmcl'
    			cmsSig1colorData 0x31434C52 '1CLR'
    			cmsSig2colorData 0x32434C52 '2CLR'
    			cmsSig3colorData 0x33434C52 '3CLR'
    			cmsSig4colorData 0x34434C52 '4CLR'
    			cmsSig5colorData 0x35434C52 '5CLR'
    			cmsSig6colorData 0x36434C52 '6CLR'
    			cmsSig7colorData 0x37434C52 '7CLR'
    			cmsSig8colorData 0x38434C52 '8CLR'
    			cmsSig9colorData 0x39434C52 '9CLR'
    			cmsSig10colorData 0x41434C52 'ACLR'
    			cmsSig11colorData 0x42434C52 'BCLR'
    			cmsSig12colorData 0x43434C52 'CCLR'
    			cmsSig13colorData 0x44434C52 'DCLR'
    			cmsSig14colorData 0x45434C52 'ECLR'
    			cmsSig15colorData 0x46434C52 'FCLR'
    			cmsSigLuvKData 0x4C75764B 'LuvK'
    """
def get_device_class(hprofile: capsule) -> int:
    """
    		Gets device class of a profile.
    
    		Parameters
    		----------
    		hp: PyCapsule
    			Profile handle
    
    		Returns
    		-------
    		int
    			cmsSigInputClass 0x73636E72 'scnr'
    			cmsSigDisplayClass 0x6D6E7472 'mntr'
    			cmsSigOutputClass 0x70727472 'prtr'
    			cmsSigLinkClass 0x6C696E6B 'link'
    			cmsSigAbstractClass 0x61627374 'abst'
    			cmsSigColorSpaceClass 0x73706163 'spac'
    			cmsSigNamedColorClass 0x6e6d636c 'nmcl' 
    """
def get_profile_description(hprofile: capsule) -> typing.Any:
    """
    		Gets profile description. eng/USA only.
    
    		Parameters
    		----------
    		hp: PyCapsule
    			Profile handle
    
    		Returns
    		-------
    		Optional[str]
    			None if error
    """
def get_transform_formatter(is_float: int, pixel_type: int, n_ch: int, n_byte: int, swap: int, extra: int) -> int:
    """
    		Calculates transform formatter.
    
    		Parameters
    		----------
    		is_float: int
    			0 or 1
    		pixel_type: int
    			Colorspace type
    			PT_ANY       0    // Don't check colorspace
    			PT_GRAY      3
    			PT_RGB       4
    			PT_CMY       5
    			PT_CMYK      6
    			PT_YCbCr     7
    			PT_YUV       8      // Lu'v'
    			PT_XYZ       9
    			PT_Lab       10
    			PT_YUVK      11     // Lu'v'K
    			PT_HSV       12
    			PT_HLS       13
    			PT_Yxy       14
    
    		n_ch: int
    			Number of channel. Alpha channel is not included here.
    
    		n_byte: int
    			Number of byte of a channel. uint16 should be 2.
    
    		swap: int
    			1 if BGR order, not RGB
    		
    		extra: int
    			1 if there is alpha channel
    """
def link_tag(hprofile: capsule, link_tag: str, dest_tag: str) -> int:
    """
    		Links a tag to another tag.
    
    		Parameters
    		----------
    		hprofile: PyCapsule
    			Profile handle
    		link_tag: str
    			AnBm or BnAm
    		dest_tag: str
    			AnBm or BnAm
    
    		Returns
    		-------
    		int
    			0 if fail
    """
def open_profile_from_mem(profile_content: bytes) -> capsule:
    """
    		Opens ICC profile from memory.
    
    		Parameters
    		----------
    		profile_content: bytes
    
    		Returns
    		-------
    		PyCapsule
    			Profile handle. None if error.
    """
def set_alarm_codes(alarm_codes: numpy.ndarray[numpy.uint16]) -> int:
    """
    		Sets the global codes used to mark out-out-gamut on Proofing transforms. Values are meant to be encoded in 16 bits.
    		Set cmsFLAGS_GAMUTCHECK and cmsFLAGS_SOFTPROOFING in create_proofing_transform().
    
    		Parameters
    		----------
    		alarm_codes: [uint16], shape=(16)
    
    		Returns
    		-------
    		int
    			0 if fail
    """
def set_log_error_handler(handler: typing.Callable) -> None:
    """
    		Set log error handler.
    
    		Parameters
    		----------
    		handler: Callable[[uint32, str], None]
    			uint32:
    				cmsERROR_UNDEFINED           0
    				cmsERROR_FILE                1
    				cmsERROR_RANGE               2
    				cmsERROR_INTERNAL            3
    				cmsERROR_NULL                4
    				cmsERROR_READ                5
    				cmsERROR_SEEK                6
    				cmsERROR_WRITE               7
    				cmsERROR_UNKNOWN_EXTENSION   8
    				cmsERROR_COLORSPACE_CHECK    9
    				cmsERROR_ALREADY_DEFINED     10
    				cmsERROR_BAD_SIGNATURE       11
    				cmsERROR_CORRUPTION_DETECTED 12
    				cmsERROR_NOT_SUITABLE        13
    			str: Error message
    """
def unset_log_error_handler() -> None:
    """
    		Unset log error handler.
    """
INTENT_ABSOLUTE_COLORIMETRIC: int = 3
INTENT_PERCEPTUAL: int = 0
INTENT_RELATIVE_COLORIMETRIC: int = 1
INTENT_SATURATION: int = 2
PT_ANY: int = 0
PT_CMY: int = 5
PT_CMYK: int = 6
PT_GRAY: int = 3
PT_HLS: int = 13
PT_HSV: int = 12
PT_Lab: int = 10
PT_RGB: int = 4
PT_XYZ: int = 9
PT_YCbCr: int = 7
PT_YUV: int = 8
PT_YUVK: int = 11
PT_Yxy: int = 14
__lcms_version__: int = 2170
__version__: str = '0.1.6'
cmsERROR_ALREADY_DEFINED: int = 10
cmsERROR_BAD_SIGNATURE: int = 11
cmsERROR_COLORSPACE_CHECK: int = 9
cmsERROR_CORRUPTION_DETECTED: int = 12
cmsERROR_FILE: int = 1
cmsERROR_INTERNAL: int = 3
cmsERROR_NOT_SUITABLE: int = 13
cmsERROR_NULL: int = 4
cmsERROR_RANGE: int = 2
cmsERROR_READ: int = 5
cmsERROR_SEEK: int = 6
cmsERROR_UNDEFINED: int = 0
cmsERROR_UNKNOWN_EXTENSION: int = 8
cmsERROR_WRITE: int = 7
cmsFLAGS_BLACKPOINTCOMPENSATION: int = 8192
cmsFLAGS_GAMUTCHECK: int = 4096
cmsFLAGS_HIGHRESPRECALC: int = 1024
cmsFLAGS_KEEP_SEQUENCE: int = 128
cmsFLAGS_NOOPTIMIZE: int = 256
cmsFLAGS_NULLTRANSFORM: int = 512
cmsFLAGS_SOFTPROOFING: int = 16384
cmsSig10colorData: int = 1094929490
cmsSig11colorData: int = 1111706706
cmsSig12colorData: int = 1128483922
cmsSig13colorData: int = 1145261138
cmsSig14colorData: int = 1162038354
cmsSig15colorData: int = 1178815570
cmsSig1colorData: int = 826494034
cmsSig2colorData: int = 843271250
cmsSig3colorData: int = 860048466
cmsSig4colorData: int = 876825682
cmsSig5colorData: int = 893602898
cmsSig6colorData: int = 910380114
cmsSig7colorData: int = 927157330
cmsSig8colorData: int = 943934546
cmsSig9colorData: int = 960711762
cmsSigAbstractClass: int = 1633842036
cmsSigCmyData: int = 1129142560
cmsSigCmykData: int = 1129142603
cmsSigColorSpaceClass: int = 1936744803
cmsSigDisplayClass: int = 1835955314
cmsSigGrayData: int = 1196573017
cmsSigHlsData: int = 1212961568
cmsSigHsvData: int = 1213421088
cmsSigInputClass: int = 1935896178
cmsSigLabData: int = 1281450528
cmsSigLinkClass: int = 1818848875
cmsSigLuvData: int = 1282766368
cmsSigLuvKData: int = 1282766411
cmsSigMCH1Data: int = 1296255025
cmsSigMCH2Data: int = 1296255026
cmsSigMCH3Data: int = 1296255027
cmsSigMCH4Data: int = 1296255028
cmsSigMCH5Data: int = 1296255029
cmsSigMCH6Data: int = 1296255030
cmsSigMCH7Data: int = 1296255031
cmsSigMCH8Data: int = 1296255032
cmsSigMCH9Data: int = 1296255033
cmsSigMCHAData: int = 1296255041
cmsSigMCHBData: int = 1296255042
cmsSigMCHCData: int = 1296255043
cmsSigMCHDData: int = 1296255044
cmsSigMCHEData: int = 1296255045
cmsSigMCHFData: int = 1296255046
cmsSigNamedColorClass: int = 1852662636
cmsSigNamedData: int = 1852662636
cmsSigOutputClass: int = 1886549106
cmsSigRgbData: int = 1380401696
cmsSigXYZData: int = 1482250784
cmsSigYCbCrData: int = 1497588338
cmsSigYxyData: int = 1501067552
