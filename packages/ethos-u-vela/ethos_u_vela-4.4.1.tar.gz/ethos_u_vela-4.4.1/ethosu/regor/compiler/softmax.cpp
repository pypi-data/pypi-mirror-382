//
// SPDX-FileCopyrightText: Copyright 2021-2025 Arm Limited and/or its affiliates <open-source-office@arm.com>
//
// SPDX-License-Identifier: Apache-2.0
//
// Licensed under the Apache License, Version 2.0 (the License); you may
// not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an AS IS BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

#include "compiler/softmax.hpp"

#include "common/numeric_util.hpp"
#include "common/scaling.hpp"
#include "operation.hpp"
#include "operation_util.hpp"

#include <fixedpoint/fixedpoint.h>
#include <algorithm>
#include <vector>

namespace regor
{

/*** Exp LUT table for int16 Softmax */
static const uint32_t EXP_LUT[] = {
    // clang-format off
    0x00000002, 0x00000002, 0x00000002, 0x00000002, 0x00000002, 0x00000002, 0x00000002, 0x00000002,
    0x00000002, 0x00000002, 0x00000002, 0x00000002, 0x00000002, 0x00000002, 0x00000002, 0x00000002,
    0x00000002, 0x00000002, 0x00000002, 0x00000002, 0x00000002, 0x00000002, 0x00000002, 0x00000002,
    0x00000002, 0x00000002, 0x00010002, 0x00000003, 0x00000003, 0x00000003, 0x00000003, 0x00000003,
    0x00000003, 0x00000003, 0x00000003, 0x00000003, 0x00000003, 0x00000003, 0x00000003, 0x00000003,
    0x00000003, 0x00000003, 0x00000003, 0x00010003, 0x00000004, 0x00000004, 0x00000004, 0x00000004,
    0x00000004, 0x00000004, 0x00000004, 0x00000004, 0x00000004, 0x00000004, 0x00000004, 0x00000004,
    0x00010004, 0x00000005, 0x00000005, 0x00000005, 0x00000005, 0x00000005, 0x00000005, 0x00000005,
    0x00000005, 0x00000005, 0x00010005, 0x00000006, 0x00000006, 0x00000006, 0x00000006, 0x00000006,
    0x00000006, 0x00000006, 0x00010006, 0x00000007, 0x00000007, 0x00000007, 0x00000007, 0x00000007,
    0x00000007, 0x00000007, 0x00010007, 0x00000008, 0x00000008, 0x00000008, 0x00000008, 0x00000008,
    0x00010008, 0x00000009, 0x00000009, 0x00000009, 0x00000009, 0x00000009, 0x00010009, 0x0000000a,
    0x0000000a, 0x0000000a, 0x0000000a, 0x0001000a, 0x0000000b, 0x0000000b, 0x0000000b, 0x0000000b,
    0x0001000b, 0x0000000c, 0x0000000c, 0x0000000c, 0x0001000c, 0x0000000d, 0x0000000d, 0x0000000d,
    0x0001000d, 0x0000000e, 0x0000000e, 0x0000000e, 0x0001000e, 0x0000000f, 0x0000000f, 0x0001000f,
    0x00000010, 0x00000010, 0x00010010, 0x00000011, 0x00000011, 0x00010011, 0x00000012, 0x00000012,
    0x00010012, 0x00000013, 0x00000013, 0x00010013, 0x00000014, 0x00010014, 0x00000015, 0x00000015,
    0x00010015, 0x00000016, 0x00010016, 0x00000017, 0x00010017, 0x00000018, 0x00010018, 0x00000019,
    0x00010019, 0x0000001a, 0x0001001a, 0x0000001b, 0x0001001b, 0x0000001c, 0x0001001c, 0x0000001d,
    0x0001001d, 0x0000001e, 0x0001001e, 0x0001001f, 0x00000020, 0x00010020, 0x00010021, 0x00000022,
    0x00010022, 0x00010023, 0x00000024, 0x00010024, 0x00000025, 0x00010025, 0x00010026, 0x00010027,
    0x00000028, 0x00020028, 0x0000002a, 0x0001002a, 0x0001002b, 0x0001002c, 0x0000002d, 0x0001002d,
    0x0001002e, 0x0001002f, 0x00010030, 0x00010031, 0x00010032, 0x00010033, 0x00010034, 0x00010035,
    0x00010036, 0x00010037, 0x00010038, 0x00020039, 0x0001003b, 0x0000003c, 0x0002003c, 0x0001003e,
    0x0002003f, 0x00000041, 0x00020041, 0x00010043, 0x00010044, 0x00020045, 0x00020047, 0x00010049,
    0x0001004a, 0x0002004b, 0x0001004d, 0x0002004e, 0x00010050, 0x00020051, 0x00020053, 0x00010055,
    0x00020056, 0x00020058, 0x0002005a, 0x0001005c, 0x0002005d, 0x0002005f, 0x00020061, 0x00020063,
    0x00020065, 0x00020067, 0x00020069, 0x0002006b, 0x0003006d, 0x00020070, 0x00020072, 0x00020074,
    0x00030076, 0x00020079, 0x0003007b, 0x0002007e, 0x00030080, 0x00020083, 0x00020085, 0x00040087,
    0x0002008b, 0x0003008d, 0x00030090, 0x00020093, 0x00030095, 0x00030098, 0x0003009b, 0x0004009e,
    0x000300a2, 0x000300a5, 0x000300a8, 0x000300ab, 0x000400ae, 0x000300b2, 0x000400b5, 0x000400b9,
    0x000300bd, 0x000400c0, 0x000400c4, 0x000400c8, 0x000400cc, 0x000400d0, 0x000500d4, 0x000400d9,
    0x000400dd, 0x000500e1, 0x000400e6, 0x000500ea, 0x000400ef, 0x000500f3, 0x000500f8, 0x000500fd,
    0x00050102, 0x00050107, 0x0005010c, 0x00060111, 0x00050117, 0x0006011c, 0x00060122, 0x00060128,
    0x0006012e, 0x00060134, 0x0006013a, 0x00070140, 0x00060147, 0x0007014d, 0x00060154, 0x0007015a,
    0x00070161, 0x00060168, 0x0008016e, 0x00070176, 0x0008017d, 0x00080185, 0x0007018d, 0x00090194,
    0x0008019d, 0x000801a5, 0x000801ad, 0x000901b5, 0x000901be, 0x000901c7, 0x000901d0, 0x000901d9,
    0x000a01e2, 0x000901ec, 0x000a01f5, 0x000b01ff, 0x000a020a, 0x000b0214, 0x000a021f, 0x000b0229,
    0x000b0234, 0x000b023f, 0x000c024a, 0x000c0256, 0x000c0262, 0x000c026e, 0x000c027a, 0x000d0286,
    0x000d0293, 0x000d02a0, 0x000e02ad, 0x000e02bb, 0x000e02c9, 0x000e02d7, 0x000f02e5, 0x000f02f4,
    0x000f0303, 0x000f0312, 0x00100321, 0x00100331, 0x00110341, 0x00100352, 0x00120362, 0x00110374,
    0x00120385, 0x00120397, 0x001203a9, 0x001303bb, 0x001303ce, 0x001403e1, 0x001403f5, 0x00140409,
    0x0015041d, 0x00150432, 0x00160447, 0x0016045d, 0x00160473, 0x00170489, 0x001704a0, 0x001904b7,
    0x001804d0, 0x001904e8, 0x00190501, 0x001a051a, 0x001a0534, 0x001b054e, 0x001b0569, 0x001c0584,
    0x001c05a0, 0x001d05bc, 0x001e05d9, 0x001e05f7, 0x001e0615, 0x00200633, 0x00200653, 0x00200673,
    0x00210693, 0x002206b4, 0x002306d6, 0x002306f9, 0x0024071c, 0x00240740, 0x00260764, 0x0026078a,
    0x002607b0, 0x002807d6, 0x002907fe, 0x00290827, 0x002a0850, 0x002a087a, 0x002c08a4, 0x002c08d0,
    0x002e08fc, 0x002e092a, 0x002f0958, 0x00310987, 0x003109b8, 0x003209e9, 0x00330a1b, 0x00340a4e,
    0x00350a82, 0x00350ab7, 0x00380aec, 0x00380b24, 0x003a0b5c, 0x003a0b96, 0x003c0bd0, 0x003d0c0c,
    0x003e0c49, 0x003f0c87, 0x00400cc6, 0x00420d06, 0x00430d48, 0x00440d8b, 0x00460dcf, 0x00480e15,
    0x00480e5d, 0x00490ea5, 0x004c0eee, 0x004d0f3a, 0x004e0f87, 0x00500fd5, 0x00511025, 0x00531076,
    0x005610c9, 0x0056111f, 0x00581175, 0x005a11cd, 0x005c1227, 0x005e1283, 0x005e12e1, 0x0061133f,
    0x006413a0, 0x00651404, 0x00671469, 0x006914d0, 0x006c1539, 0x006c15a5, 0x00701611, 0x00721681,
    0x007416f3, 0x00761767, 0x007917dd, 0x007a1856, 0x007d18d0, 0x0080194d, 0x008319cd, 0x00841a50,
    0x00881ad4, 0x00891b5c, 0x008d1be5, 0x00911c72, 0x00911d03, 0x00961d94, 0x00981e2a, 0x009c1ec2,
    0x009e1f5e, 0x00a21ffc, 0x00a4209e, 0x00a92142, 0x00ab21eb, 0x00ae2296, 0x00b22344, 0x00b523f6,
    0x00b924ab, 0x00be2564, 0x00c02622, 0x00c526e2, 0x00c827a7, 0x00cc286f, 0x00d0293b, 0x00d52a0b,
    0x00d72ae0, 0x00dd2bb7, 0x00e12c94, 0x00e62d75, 0x00eb2e5b, 0x00ef2f46, 0x00f23035, 0x00f83127,
    0x00fe321f, 0x0101331d, 0x0108341e, 0x010c3526, 0x01123632, 0x01173744, 0x011c385b, 0x01233977,
    0x01273a9a, 0x012e3bc1, 0x01343cef, 0x013a3e23, 0x01403f5d, 0x0146409d, 0x014c41e3, 0x0154432f,
    0x01594483, 0x016145dc, 0x0168473d, 0x016f48a5, 0x01764a14, 0x017d4b8a, 0x01854d07, 0x018d4e8c,
    0x01945019, 0x019d51ad, 0x01a4534a, 0x01ad54ee, 0x01b5569b, 0x01be5850, 0x01c75a0e, 0x01d05bd5,
    0x01d85da5, 0x01e35f7d, 0x01eb6160, 0x01f6634b, 0x01ff6541, 0x02096740, 0x02146949, 0x021e6b5d,
    0x02296d7b, 0x02336fa4, 0x023f71d7, 0x024a7416, 0x02567660, 0x026278b6, 0x026d7b18, 0x027a7d85
    // clang-format on
};

/*** 1/(1+X) LUT table for int16 Softmax */
static const uint32_t ONE_OVER_ONE_PLUS_X_LUT[] = {
    // clang-format off
    0xffc17fff, 0xffc07fc0, 0xffc27f80, 0xffc07f42, 0xffc17f02, 0xffc17ec3, 0xffc27e84, 0xffc27e46,
    0xffc27e08, 0xffc37dca, 0xffc27d8d, 0xffc37d4f, 0xffc37d12, 0xffc37cd5, 0xffc37c98, 0xffc47c5b,
    0xffc47c1f, 0xffc47be3, 0xffc57ba7, 0xffc57b6c, 0xffc37b31, 0xffc67af4, 0xffc57aba, 0xffc67a7f,
    0xffc57a45, 0xffc67a0a, 0xffc779d0, 0xffc67997, 0xffc6795d, 0xffc77923, 0xffc778ea, 0xffc778b1,
    0xffc87878, 0xffc77840, 0xffc87807, 0xffc877cf, 0xffc97797, 0xffc87760, 0xffc97728, 0xffc976f1,
    0xffc976ba, 0xffc87683, 0xffca764b, 0xffca7615, 0xffca75df, 0xffca75a9, 0xffca7573, 0xffcb753d,
    0xffca7508, 0xffcb74d2, 0xffcb749d, 0xffca7468, 0xffcc7432, 0xffcc73fe, 0xffcb73ca, 0xffcc7395,
    0xffcd7361, 0xffcc732e, 0xffcc72fa, 0xffcd72c6, 0xffcd7293, 0xffcd7260, 0xffcc722d, 0xffce71f9,
    0xffcd71c7, 0xffce7194, 0xffce7162, 0xffce7130, 0xffcf70fe, 0xffce70cd, 0xffce709b, 0xffcf7069,
    0xffcf7038, 0xffcf7007, 0xffcf6fd6, 0xffcf6fa5, 0xffd06f74, 0xffd06f44, 0xffd06f14, 0xffd06ee4,
    0xffd06eb4, 0xffd06e84, 0xffd16e54, 0xffd16e25, 0xffd16df6, 0xffd16dc7, 0xffd06d98, 0xffd26d68,
    0xffd16d3a, 0xffd26d0b, 0xffd26cdd, 0xffd26caf, 0xffd26c81, 0xffd26c53, 0xffd36c25, 0xffd26bf8,
    0xffd36bca, 0xffd36b9d, 0xffd36b70, 0xffd26b43, 0xffd46b15, 0xffd36ae9, 0xffd46abc, 0xffd46a90,
    0xffd46a64, 0xffd46a38, 0xffd46a0c, 0xffd469e0, 0xffd469b4, 0xffd56988, 0xffd5695d, 0xffd56932,
    0xffd56907, 0xffd568dc, 0xffd568b1, 0xffd56886, 0xffd6685b, 0xffd56831, 0xffd66806, 0xffd667dc,
    0xffd667b2, 0xffd76788, 0xffd6675f, 0xffd76735, 0xffd6670c, 0xffd766e2, 0xffd666b9, 0xffd7668f,
    0xffd86666, 0xffd6663e, 0xffd86614, 0xffd765ec, 0xffd865c3, 0xffd8659b, 0xffd86573, 0xffd8654b,
    0xffd86523, 0xffd864fb, 0xffd964d3, 0xffd864ac, 0xffd96484, 0xffd8645d, 0xffd96435, 0xffd9640e,
    0xffd963e7, 0xffd963c0, 0xffd96399, 0xffda6372, 0xffd9634c, 0xffda6325, 0xffda62ff, 0xffda62d9,
    0xffda62b3, 0xffda628d, 0xffda6267, 0xffdb6241, 0xffda621c, 0xffdb61f6, 0xffda61d1, 0xffdc61ab,
    0xffd96187, 0xffdc6160, 0xffdb613c, 0xffdb6117, 0xffdb60f2, 0xffdc60cd, 0xffdc60a9, 0xffdb6085,
    0xffdc6060, 0xffdc603c, 0xffdc6018, 0xffdc5ff4, 0xffdc5fd0, 0xffdd5fac, 0xffdc5f89, 0xffdc5f65,
    0xffdd5f41, 0xffdd5f1e, 0xffdd5efb, 0xffdd5ed8, 0xffdd5eb5, 0xffdd5e92, 0xffdd5e6f, 0xffdd5e4c,
    0xffdd5e29, 0xffde5e06, 0xffde5de4, 0xffdd5dc2, 0xffde5d9f, 0xffde5d7d, 0xffde5d5b, 0xffde5d39,
    0xffdf5d17, 0xffde5cf6, 0xffde5cd4, 0xffdf5cb2, 0xffdf5c91, 0xffde5c70, 0xffdf5c4e, 0xffdf5c2d,
    0xffde5c0c, 0xffe05bea, 0xffdf5bca, 0xffdf5ba9, 0xffdf5b88, 0xffdf5b67, 0xffe05b46, 0xffe05b26,
    0xffdf5b06, 0xffe05ae5, 0xffe05ac5, 0xffe05aa5, 0xffe05a85, 0xffe05a65, 0xffe05a45, 0xffe15a25,
    0xffe05a06, 0xffe059e6, 0xffe159c6, 0xffe159a7, 0xffe05988, 0xffe15968, 0xffe15949, 0xffe1592a,
    0xffe1590b, 0xffe158ec, 0xffe258cd, 0xffe158af, 0xffe15890, 0xffe25871, 0xffe15853, 0xffe25834,
    0xffe25816, 0xffe257f8, 0xffe157da, 0xffe257bb, 0xffe3579d, 0xffe25780, 0xffe25762, 0xffe25744,
    0xffe35726, 0xffe25709, 0xffe256eb, 0xffe356cd, 0xffe356b0, 0xffe35693, 0xffe25676, 0xffe35658,
    0xffe3563b, 0xffe3561e, 0xffe35601, 0xffe355e4, 0xffe455c7, 0xffe355ab, 0xffe4558e, 0xffe35572,
    0xffe45555, 0xffe35539, 0xffe4551c, 0xffe45500, 0xffe454e4, 0xffe454c8, 0xffe454ac, 0xffe45490,
    0xffe45474, 0xffe55458, 0xffe4543d, 0xffe45421, 0xffe55405, 0xffe553ea, 0xffe453cf, 0xffe553b3,
    0xffe45398, 0xffe5537c, 0xffe55361, 0xffe55346, 0xffe5532b, 0xffe55310, 0xffe552f5, 0xffe552da,
    0xffe652bf, 0xffe552a5, 0xffe5528a, 0xffe6526f, 0xffe55255, 0xffe6523a, 0xffe65220, 0xffe55206,
    0xffe651eb, 0xffe651d1, 0xffe651b7, 0xffe6519d, 0xffe65183, 0xffe65169, 0xffe7514f, 0xffe65136,
    0xffe6511c, 0xffe75102, 0xffe650e9, 0xffe750cf, 0xffe650b6, 0xffe7509c, 0xffe75083, 0xffe6506a,
    0xffe75050, 0xffe75037, 0xffe7501e, 0xffe75005, 0xffe74fec, 0xffe74fd3, 0xffe74fba, 0xffe74fa1,
    0xffe84f88, 0xffe74f70, 0xffe84f57, 0xffe74f3f, 0xffe84f26, 0xffe74f0e, 0xffe84ef5, 0xffe84edd,
    0xffe84ec5, 0xffe84ead, 0xffe74e95, 0xffe84e7c, 0xffe84e64, 0xffe94e4c, 0xffe84e35, 0xffe84e1d,
    0xffe84e05, 0xffe94ded, 0xffe84dd6, 0xffe84dbe, 0xffe94da6, 0xffe94d8f, 0xffe84d78, 0xffe84d60,
    0xffea4d48, 0xffe84d32, 0xffe94d1a, 0xffe94d03, 0xffe84cec, 0xffe94cd4, 0xffe94cbd, 0xffea4ca6,
    0xffe94c90, 0xffe84c79, 0xffea4c61, 0xffe94c4b, 0xffe94c34, 0xffea4c1d, 0xffe94c07, 0xffea4bf0,
    0xffe94bda, 0xffea4bc3, 0xffea4bad, 0xffe94b97, 0xffea4b80, 0xffea4b6a, 0xffea4b54, 0xffea4b3e,
    0xffea4b28, 0xffea4b12, 0xffea4afc, 0xffea4ae6, 0xffea4ad0, 0xffeb4aba, 0xffea4aa5, 0xffea4a8f,
    0xffeb4a79, 0xffea4a64, 0xffea4a4e, 0xffeb4a38, 0xffeb4a23, 0xffea4a0e, 0xffeb49f8, 0xffea49e3,
    0xffeb49cd, 0xffeb49b8, 0xffeb49a3, 0xffeb498e, 0xffea4979, 0xffeb4963, 0xffeb494e, 0xffec4939,
    0xffeb4925, 0xffea4910, 0xffec48fa, 0xffeb48e6, 0xffeb48d1, 0xffec48bc, 0xffeb48a8, 0xffec4893,
    0xffeb487f, 0xffec486a, 0xffeb4856, 0xffec4841, 0xffec482d, 0xffeb4819, 0xffec4804, 0xffec47f0,
    0xffec47dc, 0xffec47c8, 0xffec47b4, 0xffec47a0, 0xffec478c, 0xffec4778, 0xffec4764, 0xffec4750,
    0xffec473c, 0xffed4728, 0xffec4715, 0xffec4701, 0xffed46ed, 0xffec46da, 0xffed46c6, 0xffec46b3,
    0xffec469f, 0xffed468b, 0xffed4678, 0xffec4665, 0xffed4651, 0xffed463e, 0xffed462b, 0xffec4618,
    0xffed4604, 0xffed45f1, 0xffed45de, 0xffed45cb, 0xffed45b8, 0xffed45a5, 0xffed4592, 0xffed457f,
    0xffee456c, 0xffed455a, 0xffed4547, 0xffed4534, 0xffee4521, 0xffed450f, 0xffed44fc, 0xffee44e9,
    0xffed44d7, 0xffee44c4, 0xffee44b2, 0xffed44a0, 0xffee448d, 0xffee447b, 0xffed4469, 0xffee4456,
    0xffee4444, 0xffee4432, 0xffee4420, 0xffee440e, 0xffee43fc, 0xffee43ea, 0xffee43d8, 0xffee43c6,
    0xffee43b4, 0xffee43a2, 0xffee4390, 0xffef437e, 0xffee436d, 0xffee435b, 0xffef4349, 0xffee4338,
    0xffee4326, 0xffef4314, 0xffee4303, 0xffef42f1, 0xffee42e0, 0xffef42ce, 0xffee42bd, 0xffef42ab,
    0xffef429a, 0xffee4289, 0xfff04277, 0xffee4267, 0xffef4255, 0xffef4244, 0xffef4233, 0xffef4222,
    0xffee4211, 0xffef41ff, 0xfff041ee, 0xffef41de, 0xffef41cd, 0xffee41bc, 0xfff041aa, 0xffef419a,
    0xffef4189, 0xffef4178, 0xfff04167, 0xffef4157, 0xffef4146, 0xfff04135, 0xffef4125, 0xfff04114,
    0xffef4104, 0xfff040f3, 0xffef40e3, 0xfff040d2, 0xfff040c2, 0xffef40b2, 0xfff040a1, 0xfff04091,
    0xfff04081, 0xffef4071, 0xfff04060, 0xfff04050, 0xfff04040, 0xfff04030, 0xfff04020, 0xfff04010
    // clang-format on
};

Softmax::Softmax(OptimiserDatabase *db) : _db(db)
{
}

Operation *Softmax::ConvertOp(Operation *const operation)
{
    auto returnOp = operation;

    if ( OpType::Softmax == operation->Type() )
    {
        auto ifmConn = operation->Input(TensorUsage::IFM0);
        auto ofmConn = operation->Output(TensorUsage::OFM);
        auto ifm = ifmConn->tensor.get();
        auto ofm = ofmConn->tensor.get();

        if ( ifm->Type() == ofm->Type() || (ifm->Type() == DataType::Int8 && ofm->Type() == DataType::Int16) )
        {
            // Reshape if needed
            auto fullShape = Shape::PadAxes(ifmConn->shape, 4, 1);
            if ( fullShape.Batch() > 1 )
            {
                fullShape = fullShape.WithHeight(fullShape.Batch() * fullShape.Height()).WithBatch(1);
            }
            ifmConn->shape = fullShape;
            ofmConn->shape = std::move(fullShape);

            if ( ifm->Type() == DataType::Int8 || ifm->Type() == DataType::UInt8 )
            {
                returnOp = GetGraph8Bit(operation, ifmConn, ofmConn);
            }
            else if ( ifm->Type() == DataType::Int16 )
            {
                returnOp = GetGraphInt16(operation, ifmConn, ofmConn);
            }
        }
        if ( operation != returnOp )
        {
            operation->Disconnect();
        }
    }

    return returnOp;
}


void Softmax::RecordOptimisation(Operation *const operation, Operation *op)
{
    if ( _db )
    {
        _db->AddOptimised(*operation, op);
    }
}

Operation *Softmax::GetGraph8Bit(Operation *const operation, TensorConnection *ifmConn, TensorConnection *ofmConn)
{
    const auto &ifmQuant = ifmConn->quantization;
    auto *softmax = operation->Attribute<softmax_attr_t>();
    auto expTable = GenerateExpTable(double(softmax->beta), ifmQuant.scales[0].Dequantize());
    auto noScaleQuant = ifmConn->quantization;
    noScaleQuant.scales.clear();
    auto noScaleQuantZp0 = noScaleQuant;
    noScaleQuantZp0.zeroPoints[0] = 0;
    auto oneScaleQuant = ifmConn->quantization;
    oneScaleQuant.scales[0] = {1, 0};
    oneScaleQuant.zeroPoints[0] = 0;
    auto twoScaleQuant = oneScaleQuant;
    twoScaleQuant.scales[0] = {2, 0};

    // PASS 0 - Depthwise Maxpool
    auto op = CreateDepthwiseMaxpool(ifmConn->tensor, ifmConn->shape, ifmConn->quantization, noScaleQuant);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto ifmMax = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 1 - Sub
    auto subQuant = oneScaleQuant;
    subQuant.zeroPoints[0] = 127;
    op = CreateSub(ifmConn->tensor, ifmMax, ifmConn->quantization, noScaleQuant, subQuant, DataType::Int8, &ifmConn->shape);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto ifm_sub = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 1.5 - LUT(exp)
    auto expLut = CreateConstTensor("exp_lut", DataType::Int32, std::make_shared<Buffer>(std::move(expTable)));
    op = CreateLUT(ifm_sub, expLut, subQuant, subQuant);
    auto ifm_exp = op->Output(TensorUsage::OFM)->tensor;
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    RecordOptimisation(operation, op);

    // PASS 2 - ASR
    auto right_shift12 = CreateConstTensor("right_shift12", 12);
    op = CreateAsr(ifm_exp, right_shift12, subQuant, noScaleQuant, noScaleQuantZp0);
    op->Output(TensorUsage::OFM)->Set(RoundMode::NATURAL);
    op->Attribute<asr_attr_t>()->round = true;
    auto rescaled_exp = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 3 - Reduce sum
    op = CreateReduceSum(rescaled_exp, noScaleQuantZp0, noScaleQuantZp0);
    op->Output(TensorUsage::OFM)->Set(RoundMode::NATURAL);
    auto sum_of_exp = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 4 - CLZ
    op = CreateClz(sum_of_exp, noScaleQuantZp0, noScaleQuantZp0);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto headroom_plus_one = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 5 - Sub
    auto headroom_offset = CreateConstTensor("headroom_offset", 12 + 31 - DataTypeSizeBits(ofmConn->tensor->Type()));
    op = CreateSub(headroom_offset, headroom_plus_one, noScaleQuantZp0, noScaleQuantZp0, noScaleQuantZp0);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto right_shift = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 6 - Sub
    auto one = CreateConstTensor("one_const", 1);
    op = CreateSub(headroom_plus_one, one, noScaleQuantZp0, noScaleQuant, noScaleQuantZp0);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto headroom = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 7 - SHL
    op = CreateShl(sum_of_exp, headroom, noScaleQuantZp0, noScaleQuantZp0, oneScaleQuant);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto half_denominator = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 8 - Multiply
    auto neg_32_over_17 = CreateConstTensor("neg_32_over_17", -int32_t((32ULL << 29U) / 17U));
    op = CreateMul(half_denominator, neg_32_over_17, oneScaleQuant, oneScaleQuant, twoScaleQuant);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto rescaled = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 9 - Add
    auto const_48_over_17 = CreateConstTensor("const_48_over_17", int32_t((48ULL << 29U) / 17U));
    op = CreateAdd(rescaled, const_48_over_17, twoScaleQuant, noScaleQuant, oneScaleQuant);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto rescale_w_offset = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 10 - 24
    auto nr_x = std::move(rescale_w_offset);
    auto F2_one = CreateConstTensor("F2_one", 1 << 29);
    auto four = CreateConstTensor("four", 4);
    for ( int i = 0; i < 3; ++i )
    {
        // PASS 10, 15, 20 - MUL
        op = CreateMul(nr_x, half_denominator, oneScaleQuant, oneScaleQuant, twoScaleQuant);
        op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
        auto half_denominator_times_x = op->Output(TensorUsage::OFM)->tensor;
        RecordOptimisation(operation, op);

        // PASS 11, 16, 21 - SUB
        op = CreateSub(F2_one, half_denominator_times_x, noScaleQuant, twoScaleQuant, oneScaleQuant);
        op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
        auto one_minus_half_denominator_times_x = op->Output(TensorUsage::OFM)->tensor;
        RecordOptimisation(operation, op);

        // PASS 12, 17, 22 - MUL
        op = CreateMul(nr_x, one_minus_half_denominator_times_x, oneScaleQuant, oneScaleQuant, twoScaleQuant);
        op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
        auto to_rescale = op->Output(TensorUsage::OFM)->tensor;
        RecordOptimisation(operation, op);

        // PASS 13, 18, 23 - MUL
        op = CreateMul(to_rescale, four, twoScaleQuant, noScaleQuant, noScaleQuantZp0);
        op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
        auto to_add = op->Output(TensorUsage::OFM)->tensor;
        RecordOptimisation(operation, op);

        // PASS 14, 19, 24 - ADD
        op = CreateAdd(nr_x, to_add, oneScaleQuant, noScaleQuantZp0, oneScaleQuant);
        op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
        nr_x = op->Output(TensorUsage::OFM)->tensor;
        RecordOptimisation(operation, op);
    }

    // PASS 25 - Multiply
    op = CreateMul(ifm_exp, nr_x, oneScaleQuant, oneScaleQuant, oneScaleQuant);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto scaled_exp = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 26 - ASR
    auto shrOp = std::make_shared<Operation>(OpType::Asr);
    op = shrOp.get();
    op->Attribute<asr_attr_t>()->round = true;
    op->ConnectInput(TensorUsage::IFM, scaled_exp).Set(oneScaleQuant);
    op->ConnectInput(TensorUsage::IFM1, right_shift).Set(noScaleQuantZp0);
    if ( ifmConn->tensor->Type() == DataType::Int8 && ofmConn->tensor->Type() == DataType::Int16 )
    {  // Special case for int16 output zero point correction
        std::string name(op->IFM(0)->Name() + "/" + OpTypeToString(op->Type()));
        auto shr = std::make_shared<Tensor>(name, op->IFM(0)->Type());
        shr->SetStorageShape(op->Input(TensorUsage::IFM)->shape);
        op->ConnectOutput(TensorUsage::OFM, shr).Set(oneScaleQuant);
        RecordOptimisation(operation, op);

        // PASS 27 - ADD
        int32_t zp = int32_t(ofmConn->quantization.zeroPoints[0]);
        assert(zp == std::numeric_limits<int16_t>::min());
        auto addOp = std::make_shared<Operation>(OpType::Add);
        op = addOp.get();
        op->ConnectInput(TensorUsage::IFM, shr).Set(oneScaleQuant);
        op->ConnectInput(TensorUsage::IFM1, CreateConstTensor("zeroPoint", zp)).Set(noScaleQuantZp0);
        op->ConnectOutput(TensorUsage::OFM, ofmConn->tensor).Set(oneScaleQuant).Set(ofmConn->shape);
    }
    else
    {
        op->ConnectOutput(TensorUsage::OFM, ofmConn->tensor).Set(ofmConn->quantization).Set(ofmConn->shape);
    }
    op->Output(TensorUsage::OFM)->Set(RoundMode::NATURAL);
    RecordOptimisation(operation, op);

    return op;
}

Operation *Softmax::GetGraphInt16(Operation *const operation, TensorConnection *ifmConn, TensorConnection *ofmConn)
{
    auto noScaleQuant = ifmConn->quantization;
    noScaleQuant.scales.clear();

    // PASS 0 - Depthwise Maxpool
    auto op = CreateDepthwiseMaxpool(ifmConn->tensor, ifmConn->shape, ifmConn->quantization, noScaleQuant);
    op->Output(TensorUsage::OFM)->Set(RoundMode::NATURAL);
    auto ifmMax = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 1 - Sub
    op = CreateSub(ifmConn->tensor, ifmMax, ifmConn->quantization, noScaleQuant, ifmConn->quantization, DataType::Int32,
        &ifmConn->shape);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto sub1_ofm = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 2 - Mul
    auto *softmax = operation->Attribute<softmax_attr_t>();
    double beta = double(softmax->beta);
    double mul2_out_range = 10.0 / 65535.0;
    auto quant = ElementwiseMulScale<double>(ifmConn->quantization.scales[0].Dequantize(), beta, mul2_out_range);
    auto scale_quant = ifmConn->quantization;
    scale_quant.scales[0] = QuantizedScale(beta);
    auto mul2_quant = ofmConn->quantization;
    mul2_quant.scales[0] = QuantizedScale(mul2_out_range);
    auto scale = CreateConstTensor("mul2_scale", quant.scale);
    op = CreateMul(sub1_ofm, scale, ifmConn->quantization, scale_quant, mul2_quant);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto mul2_ofm = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 3 - Add
    auto const_add = CreateConstTensor("add3_const", 32767);
    op = CreateAdd(mul2_ofm, const_add, mul2_quant, noScaleQuant, mul2_quant, DataType::Int16);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto ifm_add = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 3.5 - LUT(exp)
    auto expBuf = std::make_shared<Buffer>(int(std::size(EXP_LUT)), EXP_LUT, true);
    auto expLut = CreateConstTensor("exp_lut", DataType::Int32, expBuf);
    op = CreateLUT(ifm_add, expLut, mul2_quant, mul2_quant, DataType::Int16);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto ifm_exp = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 4 - Reduce sum
    op = CreateReduceSum(ifm_exp, mul2_quant, noScaleQuant);
    op->Output(TensorUsage::OFM)->Set(RoundMode::NATURAL);
    auto sum_of_exp = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 5 - CLZ
    op = CreateClz(sum_of_exp, noScaleQuant, noScaleQuant);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto headroom_plus_one = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 6 - Sub
    auto const_31 = CreateConstTensor("const_31", 31);
    op = CreateSub(const_31, headroom_plus_one, noScaleQuant, noScaleQuant, noScaleQuant);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto reciprocal_right_shift = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 7 - SHL
    auto one = CreateConstTensor("one_const", 1);
    op = CreateShl(one, reciprocal_right_shift, noScaleQuant, noScaleQuant, noScaleQuant);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto constant_one = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 8 - Sub
    op = CreateSub(sum_of_exp, constant_one, noScaleQuant, noScaleQuant, noScaleQuant);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto sum_of_exps_minus_one = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // # PASS 9 - SHL
    op = CreateShl(sum_of_exps_minus_one, headroom_plus_one, noScaleQuant, noScaleQuant, noScaleQuant);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto shifted_sum_minus_one = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 10 - ASR
    auto shift = CreateConstTensor("shift_const", 15);
    op = CreateAsr(shifted_sum_minus_one, shift, noScaleQuant, noScaleQuant, noScaleQuant);
    op->Output(TensorUsage::OFM)->Set(RoundMode::NATURAL);
    op->Attribute<asr_attr_t>()->round = true;
    auto shifted_sum_minus_one_16 = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 11 - Sub
    auto sub11_const = CreateConstTensor("sub11_const", 32768);
    op = CreateSub(shifted_sum_minus_one_16, sub11_const, noScaleQuant, noScaleQuant, noScaleQuant, DataType::Int16);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto reciprocal_scale = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 11.5 - LUT(one over one plus x)
    auto oneOverOnePlusXBuf = std::make_shared<Buffer>(int(std::size(ONE_OVER_ONE_PLUS_X_LUT)), ONE_OVER_ONE_PLUS_X_LUT, true);
    auto oneOverOnePlusXLut = CreateConstTensor("one_over_one_plus_x_lut", DataType::Int32, oneOverOnePlusXBuf);
    op = CreateLUT(reciprocal_scale, oneOverOnePlusXLut, noScaleQuant, noScaleQuant, DataType::Int16);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    reciprocal_scale = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // # PASS 12 - Multiply
    op = CreateMul(ifm_exp, reciprocal_scale, noScaleQuant, noScaleQuant, noScaleQuant, DataType::Int32);
    op->Output(TensorUsage::OFM)->Set(RoundMode::DBL);
    auto mul_ofm = op->Output(TensorUsage::OFM)->tensor;
    RecordOptimisation(operation, op);

    // PASS 13 - ASR
    auto shrOp = std::make_shared<Operation>(OpType::Asr);
    op = shrOp.get();
    op->Attribute<asr_attr_t>()->round = true;
    op->ConnectInput(TensorUsage::IFM, mul_ofm).Set(noScaleQuant);
    op->ConnectInput(TensorUsage::IFM1, reciprocal_right_shift).Set(noScaleQuant);
    op->ConnectOutput(TensorUsage::OFM, ofmConn->tensor).Set(ofmConn->quantization).Set(ofmConn->shape);
    op->Output(TensorUsage::OFM)->Set(RoundMode::NATURAL);
    RecordOptimisation(operation, op);

    return op;
}

std::vector<int32_t> Softmax::GenerateExpTable(double beta, double inputScale)
{
    const int kTableSize = 256;
    const int kIntegerBits = 5;
    const int kSignedBits = 31;
    std::vector<int32_t> expTable(kTableSize);
    using FixedPoint = gemmlowp::FixedPoint<int32_t, kIntegerBits>;

    const double realBeta = std::min(beta * inputScale * (1 << (kSignedBits - kIntegerBits)), (1ll << kSignedBits) - 1.0);
    const auto quant = QuantizedScale(realBeta);
    const int leftShift = 31 - quant.shift;
    const int diffMin = -int(std::floor(1.0 * ((1 << kIntegerBits) - 1) * (1 << (kSignedBits - kIntegerBits)) / (1U << leftShift)));

    for ( int x = 0; x < kTableSize; ++x )
    {
        int inputDiff = x - 255;
        if ( inputDiff >= diffMin )
        {
            const int32_t inputDiffRescaled = gemmlowp::SaturatingRoundingDoublingHighMul(
                ClampToType<int32_t>(inputDiff * (1LL << leftShift)), quant.scale);
            expTable[x] = gemmlowp::exp_on_negative_values(FixedPoint::FromRaw(inputDiffRescaled)).raw();
        }
        else
        {
            expTable[x] = 0;
        }
    }

    return expTable;
}

}  // namespace regor
