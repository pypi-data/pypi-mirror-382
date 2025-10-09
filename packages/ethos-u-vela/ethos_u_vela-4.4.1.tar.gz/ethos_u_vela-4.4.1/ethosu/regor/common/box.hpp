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

#pragma once

#include "common.hpp"
#include "shape.hpp"

#include <cassert>
#include <string>

class Box
{
private:
    Shape _start;
    Shape _end;

public:
    struct Size
    {
        const Shape &_size;
        Size(const Shape &size) : _size(size){};
    };

public:
    Box() = default;

    Box(const Shape &start, const Shape &end) : _start(start), _end(end)
    {
        assert(start.Size() == end.Size());
        assert(start <= end);
    }

    Box(const Shape &start, const Box::Size &size) : _start(start), _end(start + size._size) {}

    Box(const Shape &end) : Box(end.WithZeros(), end) {}

    Shape &Start() { return _start; }
    Shape &End() { return _end; }

    const Shape &Start() const { return _start; }
    const Shape &End() const { return _end; }

    Shape SizeShape() const { return _end - _start; }

    bool Overlaps(const Box &other) const
    {
        int sz = _start.Size();
        for ( int i = 0; i < sz; ++i )
        {
            if ( !::Overlaps(_start[i], _end[i], other._start[i], other._end[i]) )
            {
                return false;
            }
        }
        return true;
    }

    void Move(const Shape &delta)
    {
        assert(delta.Size() == _start.Size());
        _start += delta;
        _end += delta;
    }

    void MoveTo(const Shape &start)
    {
        assert(start.Size() == _start.Size());
        Move(start - _start);
    }

    Box Intersection(const Box &other)
    {
        return Overlaps(other) ? Box(Shape::Max(_start, other._start), Shape::Min(_end, other._end)) : Box{};
    }

    bool operator==(const Box &other) const { return (_start == other._start) && (_end == other._end); }

    std::string ToString() const { return fmt::format("[{} - {}]", _start.ToString(), _end.ToString()); }
};
