PACKAGE_VERSION=$(uv run hatch version)
version_tag="v${PACKAGE_VERSION}"
echo "Tagging "$PACKAGE_VERSION
# git tag $version_tag
# git push origin $version_tag