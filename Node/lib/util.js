var error = function (err) {
  console.log(err.msg);
  process.exit(err.status);
}

module.exports = {
  'error': error
};