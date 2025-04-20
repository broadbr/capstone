import argostranslate.package
import argostranslate.translate

argostranslate.package.update_package_index()
packages = argostranslate.package.get_available_packages()
package_to_install = list(filter(lambda x: x.from_code == "en" and x.to_code == "fr", packages))[0]
argostranslate.package.install_from_path(package_to_install.download())

translated = argostranslate.translate.translate("Hello world!", "en", "fr")
print(translated)