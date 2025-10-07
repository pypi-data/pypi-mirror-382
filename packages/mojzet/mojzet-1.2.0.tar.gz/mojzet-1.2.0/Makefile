dist: clean
	uv build

publish :
	twine upload dist/*.tar.gz dist/*.whl

clean:
	rm -rf dist
