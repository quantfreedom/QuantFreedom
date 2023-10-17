/**
 * ArraySlicer tests
 *
 * Uses mocha/TDD and chai/assert
 */

/* global suite, setup, test, teardown */

var IndexedArray = require("../lib/index"),
    assert = require("chai").assert;

suite("Create", function () {

  // test data
  var data = [
    { name: "Alf" },
    { name: "Gabi" },
    { name: "Lars" },
    { name: "Fran" },
    { name: "Juli" },
    { name: "Gorka" },
    { name: "Bruce" },
    { name: "Ale" }
  ];

  test("with invalid index property", function () {
    var getIA = function () {
      new IndexedArray(data, "invalid");
    };
    assert.throw(getIA, Error, "Invalid index");
  });

  test("with invalid data", function () {
    var getIA = function () {
      new IndexedArray("no-data", "invalid");
    };
    assert.throw(getIA, Error, "Invalid data");
  });

  test("IA from data", function () {
    var ia = new IndexedArray(data, "name");
    assert.typeOf(ia, "object");
    assert.instanceOf(ia, IndexedArray);
  });

  test("IA from an empty array", function () {
    var ia = new IndexedArray([], "name");
    assert.typeOf(ia, "object");
    assert.instanceOf(ia, IndexedArray);
  });
});

suite("Sort array", function () {

  // test data
  var data = [
    { name: "Alf" },
    { name: "Gabi" },
    { name: "Lars" },
    { name: "Fran" },
    { name: "Juli" },
    { name: "Gorka" },
    { name: "Bruce" },
    { name: "Ale" }
  ];
  var ia = new IndexedArray(data, "name");

  test("of unsorted data", function () {
    var ret = ia.sort();
    assert.strictEqual(ia.minv, "Ale");
    assert.strictEqual(ia.maxv, "Lars");
    assert.instanceOf(ret, IndexedArray);
  });
});

suite("Get and fetch", function () {

  // test data
  var data = [
    { name: "Ale" },
    { name: "Alf" },
    { name: "Bruce" },
    { name: "Fran" },
    { name: "Gabi" },
    { name: "Gorka" },
    { name: "Juli" },
    { name: "Lars" }
  ];
  var ia = new IndexedArray(data, "name");

  test("one value", function () {
    var one = "Gabi",
        obj = ia.get(one);
    assert.strictEqual(obj.name, one);
  });

  test("another", function () {
    var one = "Juli",
        obj = ia.get(one);
    assert.strictEqual(obj.name, one);
  });

  test("the first again", function () {
    var one = "Gabi",
        ret = ia.fetch(one),
        obj = ia.get();
    assert.strictEqual(obj.name, one);
    assert.strictEqual(ret.cursor, 4);
    assert.isNull(ret.nextlow);
    assert.isNull(ret.nexthigh);
  });

  test("lower boundary", function () {
    var one = "Ale",
        ret = ia.fetch(one),
        obj = ia.get();
    assert.strictEqual(obj.name, one);
    assert.isNull(ret.nextlow);
    assert.isNull(ret.nexthigh);
  });

  test("higher boundary", function () {
    var one = "Lars",
        ret = ia.fetch(one),
        obj = ia.get();
    assert.strictEqual(obj.name, one);
    assert.isNull(ret.nextlow);
    assert.isNull(ret.nexthigh);
  });

  test("just position", function () {
    var one = "Bruce",
        ret = ia.fetch(one);
    assert.strictEqual(ret.cursor, 2);
  });

  test("chaining fetch and get", function () {
    var one = "Bruce",
        obj = ia.fetch(one).get();
    assert.strictEqual(obj.name, one);
  });

  test("non existent value", function () {
    var one = "Herman",
        ret = ia.fetch(one),
        obj = ia.get();
    assert.isNull(obj);
    assert.isNull(ret.cursor);
    assert.strictEqual(ret.nextlow, 5);
    assert.strictEqual(ret.nexthigh, 6);
  });

  test("non existent again", function () {
    var one = "Herman",
        obj = ia.get(one);
    assert.isNull(obj);
  });

  test("non other existent again", function () {
    var one = "Gonza",
        ret = ia.fetch(one),
        obj = ia.get();
    assert.isNull(obj);
    assert.isNull(ret.cursor);
    assert.strictEqual(ret.nextlow, 4);
    assert.strictEqual(ret.nexthigh, 5);
  });

  test("out of range lower", function () {
    var one = "Aaron",
        ret = ia.fetch(one),
        obj = ia.get();
    assert.isNull(obj);
    assert.isNull(ret.cursor);
    assert.isNull(ret.nextlow);
    assert.strictEqual(ret.nexthigh, 0);
  });

  test("out of range higher", function () {
    var one = "Zak",
        ret = ia.fetch(one),
        obj = ia.get();
    assert.isNull(obj);
    assert.isNull(ret.cursor);
    assert.strictEqual(ret.nextlow, 7);
    assert.isNull(ret.nexthigh);
  });
});

suite("Get with numeric indexes", function () {

  // test data
  var data = [
    { num: 10 },
    { num: 15 },
    { num: 25 },
    { num: 45 },
    { num: 60 },
    { num: 85 }
  ];
  var ia = new IndexedArray(data, "num");

  test("first", function () {
    var val = 10,
        obj = ia.get(val);
    assert.isObject(obj);
    assert.strictEqual(obj.num, val);
  });

  test("other", function () {
    var val = 60,
        obj = ia.get(val);
    assert.isObject(obj);
    assert.strictEqual(obj.num, val);
  });

  test("other", function () {
    var val = 25,
        obj = ia.get(val);
    assert.isObject(obj);
    assert.strictEqual(obj.num, val);
  });

  test("other", function () {
    var val = 15,
        obj = ia.get(val);
    assert.isObject(obj);
    assert.strictEqual(obj.num, val);
  });

  test("other", function () {
    var val = 45,
        obj = ia.get(val);
    assert.isObject(obj);
    assert.strictEqual(obj.num, val);
  });

  test("last", function () {
    var val = 85,
        obj = ia.get(val);
    assert.isObject(obj);
    assert.strictEqual(obj.num, val);
  });
});

suite("Get range", function () {

  // test data
  var data = [
    { name: "Ale" },
    { name: "Alf" },
    { name: "Bruce" },
    { name: "Fran" },
    { name: "Gabi" },
    { name: "Gorka" },
    { name: "Juli" },
    { name: "Lars" }
  ];
  var ia = new IndexedArray(data, "name");

  test("with indexes below, below", function () {
    var obj = ia.getRange("Aadvark", "Aaron");
    assert.isArray(obj);
    assert.lengthOf(obj, 0);
  });

  test("with indexes below, past first", function () {
    var obj = ia.getRange("Alan", "Alex");
    assert.lengthOf(obj, 1);
    assert.deepEqual(obj, data.slice(0, 1));
  });

  test("with indexes below, within", function () {
    var obj = ia.getRange("Aadvark", "Bruce");
    assert.lengthOf(obj, 3);
    assert.deepEqual(obj, data.slice(0, 3));
  });

  test("with indexes below, not", function () {
    var obj = ia.getRange("Aadvark", "Herman");
    assert.lengthOf(obj, 6);
    assert.deepEqual(obj, data.slice(0, 6));
  });

  test("with indexes below, above", function () {
    var obj = ia.getRange("Aadvark", "Zak");
    assert.lengthOf(obj, 8);
    assert.deepEqual(obj, data);
  });

  test("with indexes within, within", function () {
    var obj = ia.getRange("Bruce", "Gorka");
    assert.lengthOf(obj, 4);
    assert.deepEqual(obj, data.slice(2, 6));
  });

  test("with indexes within, within again", function () {
    var obj = ia.getRange("Bruce", "Gorka");
    assert.lengthOf(obj, 4);
    assert.deepEqual(obj, data.slice(2, 6));
  });

  test("with indexes within, not", function () {
    var obj = ia.getRange("Bruce", "Herman");
    assert.lengthOf(obj, 4);
    assert.deepEqual(obj, data.slice(2, 6));
  });

  test("with indexes not, within", function () {
    var obj = ia.getRange("Herman", "Lars");
    assert.lengthOf(obj, 2);
    assert.deepEqual(obj, data.slice(6, 8));
  });

  test("with indexes not, not", function () {
    var obj = ia.getRange("Bryan", "John");
    assert.lengthOf(obj, 3);
    assert.deepEqual(obj, data.slice(3, 6));
  });

  test("with indexes not, not again", function () {
    var obj = ia.getRange("Bryan", "John");
    assert.lengthOf(obj, 3);
    assert.deepEqual(obj, data.slice(3, 6));
  });

  test("with indexes not, not", function () {
    var obj = ia.getRange("Herman", "John");
    assert.isArray(obj);
    assert.lengthOf(obj, 0);
  });

  test("with indexes within, above", function () {
    var obj = ia.getRange("Bruce", "Zak");
    assert.lengthOf(obj, 6);
    assert.deepEqual(obj, data.slice(2, 8));
  });

  test("with indexes not, above", function () {
    var obj = ia.getRange("Herman", "Zak");
    assert.lengthOf(obj, 2);
    assert.deepEqual(obj, data.slice(6, 8));
  });

  test("with indexes before last, above", function () {
    var obj = ia.getRange("Ken", "Marcos");
    assert.lengthOf(obj, 1);
    assert.deepEqual(obj, data.slice(7, 8));
  });

  test("with indexes above, above", function () {
    var obj = ia.getRange("Yesi", "Zak");
    assert.isArray(obj);
    assert.lengthOf(obj, 0);
  });

  test("with inverted indexes", function () {
    var obj = ia.getRange("Gorka", "Bruce");
    assert.isArray(obj);
    assert.lengthOf(obj, 0);
  });
});

suite("Edge cases", function () {

  var ia = new IndexedArray([], "prop");

  test("fetch over an empty array", function () {
    var ret = ia.fetch("val");
    assert.strictEqual(ret, ia);
    assert.isNull(ret.cursor);
    assert.isNull(ret.nextlow);
    assert.isNull(ret.nexthigh);
  });
});

// TODO:
//   test custom compare function
//   test custom search function
