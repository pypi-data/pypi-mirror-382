# This is replaced during release process.
__version_suffix__ = "dev0"

APP_NAME = "zalando-kubectl"

KUBECTL_VERSION = "v1.33.4"
KUBECTL_SHA512 = {
    "linux": "e628239516ed6a3d07d47b451b7f42199fb5dcfb4d416f7b519235fd454e0fca3d0c273cc9c709f653a935a32c1f9fbd0a4be88f4c59d0ddcd674be2c289c8a5",
    "darwin": "ecd902e004a072eaa92d60ce81635519aaa93553313c808c0d27d15a07a1164b0cd586e271fe979e731e167daaed8b8816010bd018cb0ff16dcde9a46dcf0736",
}
STERN_VERSION = "1.30.0"
STERN_SHA256 = {
    "linux": "ea1bf1f1dddf1fd4b9971148582e88c637884ac1592dcba71838a6a42277708b",
    "darwin": "4eaf8f0d60924902a3dda1aaebb573a376137bb830f45703d7a0bd89e884494a",
}
KUBELOGIN_VERSION = "v1.34.1"
KUBELOGIN_SHA256 = {
    "linux": "018226f75b7f5f3223e5d46df3af746a778315fa2ea10c422cd4ead086173c96",
    "darwin": "ab30b3c7b84f5185e2c39ff4a7e7569fb227e9f8b88e2f49f5a35bb7ade6e201",
}
ZALANDO_AWS_CLI_VERSION = "1.1.2"
ZALANDO_AWS_CLI_SHA256 = {
    "linux": "d0dc1bbbab2a5c94d5e16aa8d90f38d40dc16c03fc552ed03c57871b6ec33c2c",
    "darwin": "baae4a2b2b738f34bfa7202eb56448ded76b8ef3cca1a8990f9f334978be63f2",
}

APP_VERSION = KUBECTL_VERSION + "." + __version_suffix__
